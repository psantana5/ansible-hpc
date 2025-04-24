# Spack Architecture-Specific Optimization Verification

This document explains how to verify that Spack is correctly configured for 
architecture-specific optimizations on this system.

## Detected Architecture Information

- CPU Model: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
- Architecture Target: x86_64
- Compiler Flags: -march=native -mtune=native -O3 -mavx2

## Verification Commands

Run the following commands to verify the architecture-specific configuration:

### 1. Check the detected architecture

```bash
source /opt/spack/share/spack/setup-env.sh
spack arch
```

This shows the complete architecture specification Spack is using.

### 2. View available targets for your system

```bash
source /opt/spack/share/spack/setup-env.sh
spack arch --known-targets
```

This displays all microarchitecture targets Spack recognizes for your system.

### 3. Check compiler flags being used

```bash
source /opt/spack/share/spack/setup-env.sh
spack compiler info gcc
```

This shows the compiler configuration, including optimization flags.

### 4. Examine the Spack configuration files

```bash
cat /opt/spack/etc/spack/config.yaml
cat /opt/spack/etc/spack/packages.yaml
cat /opt/spack/etc/spack/compilers.yaml
```

These files show the architecture-specific settings that were applied.

### 5. Test a package installation with verbose output

```bash
source /opt/spack/share/spack/setup-env.sh
spack install --verbose openmpi
```

The verbose output shows the exact compiler flags used during compilation.

### 6. Check how a specific package would be built

```bash
source /opt/spack/share/spack/setup-env.sh
spack spec -I openmpi
```

This shows the complete specification for how OpenMPI would be built.

## Interpreting Results

- The architecture should match your CPU (x86_64)
- Compiler flags should include architecture-specific optimizations (-march=native -mtune=native -O3 -mavx2)
- Package specs should show these optimizations are being applied
