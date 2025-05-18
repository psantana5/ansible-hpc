# 0.7 Ayuda con troubleshooting

Esta sección proporciona soluciones a problemas comunes que pueden surgir durante la implementación y uso de los diferentes componentes del clúster HPC gestionado con Ansible.

## Problemas comunes con Spack

### Error: No se puede encontrar el directorio de instalación de Spack

**Síntoma**: El playbook falla con un error indicando que no puede encontrar el directorio de Spack.

**Solución**:
1. Verifique que la variable `spack_install_dir` está correctamente definida en `inventory/group_vars/all/main.yml`
2. Asegúrese de que el playbook `spack.yml` se ha ejecutado correctamente
3. Compruebe los permisos del directorio:
   ```bash
   ls -la {{ spack_install_dir }}
   ```
4. Si el directorio no existe, ejecute nuevamente el playbook con mayor verbosidad:
   ```bash
   ansible-playbook -v spack.yml
   ```

### Error: Fallo en la creación de módulos

**Síntoma**: La tarea post_task "Create module files for installed packages" falla.

**Solución**:
1. Verifique que Spack está correctamente instalado y configurado:
   ```bash
   source {{ spack_install_dir }}/share/spack/setup-env.sh
   spack --version
   ```
2. Compruebe que los paquetes están instalados:
   ```bash
   spack find
   ```
3. Intente ejecutar el comando manualmente en uno de los nodos:
   ```bash
   source {{ spack_install_dir }}/share/spack/setup-env.sh
   spack module tcl refresh --delete-tree -y
   ```
4. Verifique los permisos del directorio de módulos.

### Error: Problemas con la detección de arquitectura

**Síntoma**: Spack no detecta correctamente la arquitectura del sistema o no aplica las optimizaciones específicas.

**Solución**:
1. Ejecute el script de verificación de arquitectura:
   ```bash
   {{ spack_install_dir }}/bin/verify-arch-optimizations.sh
   ```
2. Verifique la arquitectura detectada:
   ```bash
   source {{ spack_install_dir }}/share/spack/setup-env.sh
   spack arch
   ```
3. Compruebe los targets disponibles:
   ```bash
   source {{ spack_install_dir }}/share/spack/setup-env.sh
   spack arch --known-targets
   ```
4. Si la arquitectura no se detecta correctamente, puede especificarla manualmente en `config.yaml`:
   ```yaml
   packages:
     all:
       target: [tu_arquitectura]
   ```

### Error: Problemas con NFS y Spack

**Síntoma**: Errores al acceder a Spack desde nodos que montan el directorio por NFS.

**Solución**:
1. Verifique que el servidor NFS está exportando correctamente el directorio:
   ```bash
   showmount -e [servidor_nfs]
   ```
2. Compruebe que los nodos cliente están montando correctamente el directorio:
   ```bash
   mount | grep spack
   ```
3. Verifique los permisos en el servidor NFS:
   ```bash
   ls -la /apps/spack
   ```
4. Asegúrese de que el archivo `/etc/exports` en el servidor NFS contiene la línea correcta:
   ```
   /apps/spack *(rw,sync,no_root_squash,no_subtree_check)
   ```
5. Reinicie el servicio NFS si es necesario:
   ```bash
   exportfs -ra
   ```

### Error: Conflictos de dependencias

**Síntoma**: Errores al instalar paquetes debido a conflictos de dependencias.

**Solución**:
1. Utilice `spack spec` para ver las dependencias completas:
   ```bash
   source {{ spack_install_dir }}/share/spack/setup-env.sh
   spack spec -I [paquete]
   ```
2. Intente instalar con una versión específica:
   ```bash
   spack install [paquete]@[versión]
   ```
3. Utilice `spack concretize` para resolver dependencias sin instalar:
   ```bash
   spack concretize -f [paquete]
   ```
4. Modifique `packages.yaml` para preferir versiones específicas:
   ```yaml
   packages:
     [paquete]:
       version: [versión_preferida]
   ```

## Verificación del entorno

Para verificar que Spack está correctamente configurado y optimizado para su arquitectura, puede utilizar los siguientes comandos:

```bash
source {{ spack_install_dir }}/share/spack/setup-env.sh
spack arch                    # Muestra la arquitectura detectada
spack arch --known-targets    # Muestra los targets disponibles
spack compiler info gcc       # Muestra la configuración del compilador
spack config get config       # Muestra la configuración actual
spack config get packages     # Muestra la configuración de paquetes
```

Consulte el archivo `{{ spack_install_dir }}/ARCHITECTURE_CHECKS.md` para obtener información detallada sobre cómo verificar las optimizaciones específicas de arquitectura.

## Problemas comunes con SLURM

### Error: El servicio slurmctld no inicia

**Síntoma**: El servicio slurmctld falla al iniciar o se detiene inesperadamente.

**Solución**:
1. Verifique la configuración en `/etc/slurm/slurm.conf`:
   ```bash
   grep -n ERROR /var/log/slurm/slurmctld.log
   ```
2. Compruebe que los directorios especificados en la configuración existen y tienen los permisos correctos:
   ```bash
   ls -la /var/spool/slurm
   ls -la /var/log/slurm
   ```
3. Verifique que el usuario `slurm` existe y tiene los permisos adecuados:
   ```bash
   id slurm
   ```
4. Intente iniciar el servicio en modo debug:
   ```bash
   slurmctld -D -vvv
   ```

### Error: Los trabajos quedan en estado pendiente

**Síntoma**: Los trabajos enviados a SLURM quedan en estado pendiente indefinidamente.

**Solución**:
1. Verifique el estado de los nodos:
   ```bash
   sinfo -R    # Muestra nodos en estado DOWN o DRAIN
   scontrol show nodes
   ```
2. Compruebe las razones por las que los trabajos están pendientes:
   ```bash
   squeue -u [usuario] -l
   scontrol show job [jobid]
   ```
3. Verifique la comunicación entre los nodos y el controlador:
   ```bash
   ping [nodo_compute]
   ssh [nodo_compute] ping [nodo_controller]
   ```
4. Compruebe que slurmd está ejecutándose en los nodos de cómputo:
   ```bash
   ssh [nodo_compute] systemctl status slurmd
   ```

### Error: Problemas con la contabilidad de SLURM

**Síntoma**: No se registran correctamente los trabajos en la base de datos de contabilidad.

**Solución**:
1. Verifique que slurmdbd está ejecutándose:
   ```bash
   systemctl status slurmdbd
   ```
2. Compruebe la conexión a la base de datos:
   ```bash
   mysql -u slurm -p -h [host_db]
   ```
3. Verifique los logs de slurmdbd:
   ```bash
   tail -f /var/log/slurm/slurmdbd.log
   ```
4. Reinicie los servicios en el orden correcto:
   ```bash
   systemctl restart slurmdbd
   systemctl restart slurmctld
   ```

## Problemas comunes con OpenLDAP

### Error: No se puede conectar al servidor LDAP

**Síntoma**: Los comandos ldapsearch o ldapadd fallan con errores de conexión.

**Solución**:
1. Verifique que el servicio slapd está ejecutándose:
   ```bash
   systemctl status slapd
   ```
2. Compruebe la configuración del firewall:
   ```bash
   ss -tulpn | grep 389
   ```
3. Intente una conexión básica:
   ```bash
   ldapsearch -x -H ldap://localhost -b "" -s base
   ```
4. Verifique los logs del sistema:
   ```bash
   journalctl -u slapd
   ```

### Error: Problemas de autenticación LDAP

**Síntoma**: Los usuarios no pueden autenticarse en el sistema usando credenciales LDAP.

**Solución**:
1. Verifique la configuración de SSSD:
   ```bash
   cat /etc/sssd/sssd.conf
   ```
2. Compruebe que el servicio SSSD está ejecutándose:
   ```bash
   systemctl status sssd
   ```
3. Pruebe la resolución de usuarios:
   ```bash
   getent passwd [usuario]
   id [usuario]
   ```
4. Verifique los logs de SSSD:
   ```bash
   tail -f /var/log/sssd/sssd_[DOMINIO].log
   ```

### Error: Replicación LDAP fallando

**Síntoma**: La replicación entre servidores LDAP no funciona correctamente.

**Solución**:
1. Verifique el estado de la replicación:
   ```bash
   ldapsearch -x -H ldap://[servidor_primario] -b "cn=config" "(olcSyncrepl=*)"
   ```
2. Compruebe la conectividad entre servidores:
   ```bash
   ping [servidor_secundario]
   telnet [servidor_secundario] 389
   ```
3. Verifique los logs en ambos servidores:
   ```bash
   journalctl -u slapd
   ```
4. Reinicie el proceso de replicación si es necesario:
   ```bash
   systemctl restart slapd
   ```

## Problemas comunes con NFS

### Error: No se pueden montar los directorios compartidos

**Síntoma**: Los nodos cliente no pueden montar los directorios NFS.

**Solución**:
1. Verifique que el servidor NFS está exportando los directorios:
   ```bash
   showmount -e [servidor_nfs]
   ```
2. Compruebe la configuración del firewall en el servidor:
   ```bash
   ss -tulpn | grep -E "2049|111"
   ```
3. Intente montar manualmente:
   ```bash
   mount -t nfs [servidor_nfs]:/[ruta_exportada] /[punto_montaje]
   ```
4. Verifique los logs del sistema:
   ```bash
   dmesg | grep nfs
   ```

### Error: Rendimiento lento en NFS

**Síntoma**: Las operaciones de lectura/escritura en directorios NFS son extremadamente lentas.

**Solución**:
1. Verifique las opciones de montaje actuales:
   ```bash
   cat /proc/mounts | grep nfs
   ```
2. Optimice las opciones de montaje:
   ```bash
   mount -o remount,rw,noatime,nodiratime,rsize=131072,wsize=131072 [servidor_nfs]:/[ruta] /[punto_montaje]
   ```
3. Compruebe la carga de red:
   ```bash
   iftop -i [interfaz]
   ```
4. Considere utilizar NFS sobre RDMA si el hardware lo soporta.

## Problemas comunes con el sistema de monitoreo

### Error: Prometheus no recopila métricas

**Síntoma**: No se ven datos en los dashboards de Grafana o Prometheus muestra errores de scraping.

**Solución**:
1. Verifique que los exporters están ejecutándose:
   ```bash
   systemctl status node_exporter
   systemctl status slurm_exporter
   ```
2. Compruebe la configuración de Prometheus:
   ```bash
   curl http://localhost:9090/api/v1/targets
   ```
3. Verifique los logs de Prometheus:
   ```bash
   journalctl -u prometheus
   ```
4. Compruebe la conectividad a los exporters:
   ```bash
   curl http://[nodo]:9100/metrics
   ```

### Error: Grafana no muestra datos

**Síntoma**: Los dashboards de Grafana aparecen vacíos o con errores.

**Solución**:
1. Verifique la conexión entre Grafana y Prometheus:
   ```bash
   curl -I http://[prometheus_host]:9090/api/v1/query?query=up
   ```
2. Compruebe la configuración de la fuente de datos en Grafana:
   ```bash
   curl -H "Authorization: Bearer [api_key]" http://[grafana_host]:3000/api/datasources
   ```
3. Verifique los logs de Grafana:
   ```bash
   journalctl -u grafana-server
   ```
4. Reinicie el servicio de Grafana:
   ```bash
   systemctl restart grafana-server
   ```

## Recursos adicionales

- [Documentación oficial de Spack](https://spack.readthedocs.io/)
- [Guía de resolución de problemas de Spack](https://spack.readthedocs.io/en/latest/getting_started.html#troubleshooting)
- [Foro de la comunidad Spack](https://spack.io/community/)
- [Documentación de SLURM](https://slurm.schedmd.com/documentation.html)
- [Wiki de OpenLDAP](https://www.openldap.org/doc/)
- [Documentación de Prometheus](https://prometheus.io/docs/)
- [Documentación de Grafana](https://grafana.com/docs/)