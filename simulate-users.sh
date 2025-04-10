#!/bin/bash

# ==============================================================================
# Script para Simular Actividad de SLURM con Usuarios Existentes (v3)
#
# Descripción:
#   Este script simula el envío de trabajos SLURM por parte de un conjunto
#   aleatorio de usuarios existentes. Utiliza `sbatch` y `sudo -u <usuario>`
#   para ejecutar los trabajos como si fueran enviados por esos usuarios.
#   Selecciona aleatoriamente una partición SLURM *disponible* para cada usuario.
#   El objetivo es generar datos de accounting para probar sistemas de reporting.
#
# Mejoras v3:
#   - Ejemplo explícito de configuración sudoers en comentarios y errores.
#   - Idempotencia básica: Previene la ejecución simultánea de múltiples
#     instancias del script usando un archivo de bloqueo (lock file).
#
# Requisitos:
#   - SLURM configurado y operativo.
#   - Usuarios listados en `ALL_USERS` deben existir en el sistema.
#   - El usuario que ejecuta este script necesita permisos sudo (NOPASSWD)
#     para ejecutar `sbatch` como los usuarios de `ALL_USERS`.
#     Ejemplo /etc/sudoers.d/slurm_simulator:
#       runner_user ALL=(psantana,jsmith,...) NOPASSWD: /usr/bin/sbatch
#     (Reemplaza 'runner_user' con el usuario que ejecuta este script y
#      la lista de usuarios con los de ALL_USERS si es necesario).
#   - Herramientas: bash, sbatch, shuf, awk, grep, sudo, sleep, dd, sinfo, ps, rm
#     (y 'stress' si se activa su carga de trabajo).
#
# Autor: [Tu Nombre/Organización]
# Fecha: [Fecha Actual]
# ==============================================================================

# --- Configuración ---

# Número de usuarios aleatorios a seleccionar para la simulación
NUM_SIMULATED_USERS=5

# Número de trabajos a simular por cada usuario seleccionado
JOBS_PER_USER=3

# Ruta al ejecutable de sbatch (normalmente en el PATH, pero se puede especificar)
SBATCH_CMD="/usr/bin/sbatch" # Ajusta si es necesario

# Archivo de bloqueo para prevenir ejecuciones simultáneas
LOCK_FILE="/tmp/simulate_slurm_activity.lock"

# Lista completa de usuarios elegibles para la simulación
# Estos usuarios DEBEN existir en el sistema.
ALL_USERS=(
    # HPC-admins
    "psantana" "jsmith" "rjohnson"
    # cfes
    "mgarcia" "dwilliams" "lbrown" "tlee"
    # quantum-physics
    "kfeynman" "sbohr" "hheisenberg" "ddirac"
    # particle-physics
    "ehiggs" "mplanck" "aeinstein" "cyang"
    # astrophysics
    "shawking" "ntyson" "csagan" "jkaku"
    # condensed-matter
    "landerson" "bcooper" "jbardeen" "rfeynman"
)

# Contadores para resumen
declare -i total_jobs_attempted=0
declare -i total_jobs_succeeded=0
declare -i total_jobs_failed=0

# --- Opciones de Bash ---
set -o pipefail # Hace que un pipeline falle si cualquier comando en él falla

# --- Funciones ---

# Función para verificar la existencia de comandos necesarios
check_command() {
    local cmd=$1
    if ! command -v "$cmd" &> /dev/null; then
        # Si el comando es el propio sbatch, usar la variable SBATCH_CMD
        if [[ "$cmd" == "sbatch" && -x "$SBATCH_CMD" ]]; then
            return 0 # Encontrado a través de la ruta explícita
        fi
        echo "ERROR: Comando requerido '$cmd' no encontrado. Instálalo o verifica el PATH." >&2
        # Limpiar lock si se creó antes de salir por comando faltante
        rm -f "$LOCK_FILE"
        exit 1
    fi
}

# Función para obtener una lista de particiones SLURM disponibles (estado 'up')
get_available_partitions() {
    local partitions
    partitions=$(sinfo -h -o "%P %a" | awk '$2 == "up" {print $1}')
    if [[ -z "$partitions" ]]; then
        echo "ERROR: No se encontraron particiones SLURM en estado 'up'. Verifica 'sinfo'." >&2
        return 1
    fi
    echo "$partitions"
    return 0
}

# Función de limpieza: se ejecuta al salir del script (normal, error, señal)
cleanup() {
    echo "Limpiando y saliendo..."
    rm -f "$LOCK_FILE"
    echo "Archivo de bloqueo eliminado."
}

# --- Idempotencia: Verificación de Bloqueo ---
# Asociar la función cleanup a las señales EXIT, INT, TERM
trap cleanup EXIT SIGINT SIGTERM

echo "--- Verificación de Bloqueo ---"
# Comprobar si el archivo de bloqueo existe
if [ -e "$LOCK_FILE" ]; then
    # Leer el PID del proceso que creó el lock
    LOCKED_PID=$(cat "$LOCK_FILE")
    # Comprobar si ese proceso todavía está en ejecución
    if ps -p "$LOCKED_PID" > /dev/null; then
        echo "ERROR: El script ya está en ejecución (PID: $LOCKED_PID)." >&2
        echo "       Archivo de bloqueo encontrado: $LOCK_FILE" >&2
        echo "       Si estás seguro de que no hay otra instancia ejecutándose," >&2
        echo "       elimina manualmente el archivo: rm -f $LOCK_FILE" >&2
        exit 1 # Salir porque otra instancia está activa
    else
        echo "WARN: Se encontró un archivo de bloqueo obsoleto (PID $LOCKED_PID no existe). Eliminándolo." >&2
        rm -f "$LOCK_FILE"
    fi
fi

# Crear el archivo de bloqueo con el PID del proceso actual
echo $$ > "$LOCK_FILE"
if [[ $? -ne 0 ]]; then
    echo "ERROR: No se pudo crear el archivo de bloqueo '$LOCK_FILE'. Verifica permisos en /tmp/." >&2
    exit 1
fi
echo "[OK] Archivo de bloqueo creado: $LOCK_FILE (PID: $$)"


# --- Verificaciones Preliminares ---

echo -e "\n--- Verificaciones Preliminares ---"

# Verificar herramientas esenciales (incluyendo las usadas en lock check y sbatch)
for cmd in sbatch shuf sudo sleep dd sinfo awk grep ps rm; do
    check_command "$cmd"
done
echo "[OK] Herramientas básicas encontradas."

# Verificar si 'stress' está disponible (opcional)
if ! command -v stress &> /dev/null; then
    echo "[WARN] Comando 'stress' no encontrado. La carga de trabajo de CPU usará 'sleep' como alternativa."
fi

# Verificar permisos sudo NOPASSWD para sbatch
echo "Verificando permisos sudo NOPASSWD para '$SBATCH_CMD'..."
FIRST_USER_TO_TEST="${ALL_USERS[0]}"
if [[ -z "$FIRST_USER_TO_TEST" ]]; then
   echo "ERROR: La lista ALL_USERS está vacía." >&2
   exit 1 # La limpieza se activará con trap
fi

# Intentar ejecutar 'sbatch --version' como el primer usuario sin pedir contraseña
if sudo -n -u "$FIRST_USER_TO_TEST" "$SBATCH_CMD" --version > /dev/null 2>&1; then
    echo "[OK] Permisos sudo NOPASSWD parecen configurados correctamente para '$FIRST_USER_TO_TEST' y '$SBATCH_CMD'."
else
    CURRENT_USER=$(whoami)
    echo "--------------------------------------------------------------------" >&2
    echo "ERROR: Falló la prueba de 'sudo -n -u $FIRST_USER_TO_TEST $SBATCH_CMD --version'." >&2
    echo "       Asegúrate de que el usuario '$CURRENT_USER' tenga permisos sudo NOPASSWD" >&2
    echo "       para ejecutar '$SBATCH_CMD' como los usuarios en ALL_USERS." >&2
    echo ""
    echo "       Ejemplo de configuración requerida en /etc/sudoers o /etc/sudoers.d/slurm_simulator :" >&2
    echo "       $CURRENT_USER ALL=(${ALL_USERS[*]}) NOPASSWD: $SBATCH_CMD" >&2
    echo ""
    echo "       (Reemplaza '$CURRENT_USER' si es necesario y la lista de usuarios si la tuya difiere)." >&2
    echo "--------------------------------------------------------------------" >&2
    exit 1 # La limpieza se activará con trap
fi

# Obtener lista inicial de particiones disponibles
echo "Verificando particiones SLURM disponibles..."
AVAILABLE_PARTITIONS=$(get_available_partitions)
if [[ $? -ne 0 ]]; then
    # La función ya imprimió el error
    exit 1 # La limpieza se activará con trap
fi
NUM_AVAILABLE_PARTITIONS=$(echo "$AVAILABLE_PARTITIONS" | wc -l)
echo "[OK] Encontradas $NUM_AVAILABLE_PARTITIONS particiones disponibles: $(echo "$AVAILABLE_PARTITIONS" | paste -sd, -)"

# --- Selección Aleatoria de Usuarios ---

echo -e "\n--- Selección de Usuarios ---"

if [ ${#ALL_USERS[@]} -lt $NUM_SIMULATED_USERS ]; then
    echo "ERROR: Se solicitaron $NUM_SIMULATED_USERS usuarios, pero solo hay ${#ALL_USERS[@]} disponibles en la lista." >&2
    exit 1 # La limpieza se activará con trap
fi

SELECTED_USERS=($(shuf -e "${ALL_USERS[@]}" -n $NUM_SIMULATED_USERS))
echo "Usuarios seleccionados para la simulación (${#SELECTED_USERS[@]}): ${SELECTED_USERS[*]}"

# --- Simulación de Envío de Trabajos ---

echo -e "\n--- Simulación de Trabajos SLURM ---"

for user in "${SELECTED_USERS[@]}"; do
    CURRENT_AVAILABLE_PARTITIONS=$(get_available_partitions)
    if [[ $? -ne 0 || -z "$CURRENT_AVAILABLE_PARTITIONS" ]]; then
        echo "ERROR: No se pudieron obtener particiones disponibles para el usuario '$user' en este momento. Saltando..." >&2
        continue
    fi

    selected_partition=$(echo "$CURRENT_AVAILABLE_PARTITIONS" | shuf -n 1)
    echo -e "\nSimulando $JOBS_PER_USER trabajos para usuario: '$user' en Partición: '$selected_partition'"

    for (( i=1; i<=JOBS_PER_USER; i++ )); do
        ((total_jobs_attempted++))
        job_tag="sim_${user}_${i}_${RANDOM}"
        runtime_min=$(shuf -i 1-15 -n 1)
        runtime_sec=$(shuf -i 0-59 -n 1)
        cpus=$(shuf -i 1-4 -n 1)
        mem_per_cpu=$(shuf -i 100-1024 -n 1)
        workload_type=$(( RANDOM % 3 ))

        read -r -d '' SLURM_SCRIPT <<EOF
#!/bin/bash
#SBATCH --job-name=${job_tag}
#SBATCH --output=/tmp/${job_tag}_%j.out
#SBATCH --error=/tmp/${job_tag}_%j.err
#SBATCH --partition=${selected_partition}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=${cpus}
#SBATCH --mem-per-cpu=${mem_per_cpu}M
#SBATCH --time=00:${runtime_min}:${runtime_sec}
#SBATCH --comment="Simulated job for reporting test by script $$"

echo "-----------------------------------------------------"
echo "SLURM Job ID: \$SLURM_JOB_ID"
echo "Ejecutando como usuario: \$(whoami)"
echo "Enviado por (simulado): $user"
echo "Nodo: \$(hostname)"
echo "Partición: \$SLURM_JOB_PARTITION"
echo "Fecha y hora: \$(date)"
echo "CPUs solicitadas: \$SLURM_CPUS_PER_TASK"
echo "Memoria por CPU solicitada: \$SLURM_MEM_PER_CPU MB"
echo "Tiempo límite: ${runtime_min}m ${runtime_sec}s"
echo "-----------------------------------------------------"
echo ""
echo "Iniciando carga de trabajo simulada (Tipo: $workload_type)..."

case $workload_type in
    0) # Sleep
        sleep_duration=\$(( ${runtime_min} * 60 + ${runtime_sec} - 10 ))
        [ \$sleep_duration -lt 5 ] && sleep_duration=5
        echo "Tarea: sleep por \$sleep_duration segundos..."
        sleep \$sleep_duration
        ;;
    1) # dd
        dd_count=\$(shuf -i 50-200 -n 1)
        echo "Tarea: dd if=/dev/zero of=/dev/null bs=1M count=\${dd_count} ..."
        dd if=/dev/zero of=/dev/null bs=1M count=\${dd_count} status=none
        sleep 5
        ;;
    2) # stress / sleep fallback
        if command -v stress &> /dev/null; then
            stress_duration=\$(( (${runtime_min} * 60 + ${runtime_sec}) / 2 ))
            [ \$stress_duration -lt 10 ] && stress_duration=10
            echo "Tarea: stress --cpu ${cpus} --timeout \${stress_duration}s ..."
            stress --cpu ${cpus} --timeout \${stress_duration}s
        else
            echo "Tarea: 'stress' no encontrado, usando 'sleep'."
            sleep_duration=\$(( ${runtime_min} * 60 + ${runtime_sec} - 10 ))
            [ \$sleep_duration -lt 5 ] && sleep_duration=5
            sleep \$sleep_duration
        fi
        ;;
esac

echo "Carga de trabajo simulada completada."
echo "Fin del trabajo: \$(date)"
EOF

        echo "  [${i}/${JOBS_PER_USER}] Enviando trabajo para '$user' (Job: ${job_tag}, P:${selected_partition}, C:${cpus}, M:${mem_per_cpu}M, T:${runtime_min}m)..."
        if echo "$SLURM_SCRIPT" | sudo -n -u "$user" "$SBATCH_CMD"; then
            echo "      -> [OK] Trabajo enviado."
            ((total_jobs_succeeded++))
        else
            job_exit_code=$?
            echo "      -> [ERROR] Falló el envío del trabajo para '$user' (código de salida: $job_exit_code)." >&2
            echo "          Verifica permisos del usuario '$user' en la partición '$selected_partition', límites, o logs de slurmctld." >&2
            ((total_jobs_failed++))
        fi
        sleep 0.2
    done
done

# --- Resumen Final ---
# La limpieza (eliminar lock) se ejecutará automáticamente por el trap EXIT

echo -e "\n--- Simulación Completada ---"
echo "Resumen:"
echo "  Usuarios simulados: ${#SELECTED_USERS[@]} (${SELECTED_USERS[*]})"
echo "  Intentos de envío totales: $total_jobs_attempted"
echo "  Envíos exitosos: $total_jobs_succeeded"
echo "  Envíos fallidos: $total_jobs_failed"
echo ""
if [[ $total_jobs_succeeded -gt 0 ]]; then
    echo "Puedes verificar el estado de los trabajos con: squeue -u $(echo "${SELECTED_USERS[*]}" | tr ' ' ',')"
    echo "Una vez completados, aparecerán en el accounting (sacct)."
    echo "Archivos de salida/error en: /tmp/sim_...*.out/err"
else
    echo "No se enviaron trabajos con éxito."
fi

# Salir con código apropiado
if [[ $total_jobs_failed -gt 0 ]]; then
    exit 1
else
    exit 0
fi