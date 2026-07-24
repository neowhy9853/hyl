# PCAT-Bench-220 case distribution

## Labels

| Label | Count | Share |
|---|---:|---:|
| positive | 133 | 60.5% |
| negative | 87 | 39.5% |

## Repository distribution

| Repository | Total | Positive | Negative | False-positive boundary | Share |
|---|---:|---:|---:|---:|---:|
| cpython | 23 | 12 | 11 | 0 | 10.5% |
| kernel | 23 | 13 | 10 | 0 | 10.5% |
| git | 18 | 10 | 8 | 1 | 8.2% |
| dnsmasq | 17 | 9 | 8 | 0 | 7.7% |
| go | 16 | 9 | 7 | 0 | 7.3% |
| haproxy | 12 | 6 | 6 | 0 | 5.5% |
| libsoup | 12 | 10 | 2 | 1 | 5.5% |
| httpd | 11 | 9 | 2 | 0 | 5.0% |
| glib2 | 10 | 6 | 4 | 1 | 4.5% |
| grub2 | 10 | 8 | 2 | 0 | 4.5% |
| networkmanager | 10 | 6 | 4 | 1 | 4.5% |
| vim | 10 | 6 | 4 | 1 | 4.5% |
| rsyslog | 9 | 5 | 4 | 1 | 4.1% |
| ruby | 9 | 6 | 3 | 0 | 4.1% |
| dnf | 8 | 5 | 3 | 0 | 3.6% |
| lvm2 | 8 | 5 | 3 | 1 | 3.6% |
| openldap | 8 | 5 | 3 | 0 | 3.6% |
| libxml2 | 6 | 3 | 3 | 0 | 2.7% |

## Positive compatibility types

| Type | Count | Share of Positive |
|---|---:|---:|
| CONFIG_CLI_BEHAVIOR_CHANGE | 26 | 19.5% |
| INPUT_CONTRACT_CHANGE | 23 | 17.3% |
| OUTPUT_FORMAT_CHANGE | 14 | 10.5% |
| SIDE_EFFECT_CHANGE | 14 | 10.5% |
| API_SIGNATURE_CHANGE | 13 | 9.8% |
| ERROR_EXCEPTION_CHANGE | 13 | 9.8% |
| ABI_CHANGE | 10 | 7.5% |
| PERFORMANCE_RESOURCE_SEMANTIC_CHANGE | 5 | 3.8% |
| RESOURCE_LIFETIME_CHANGE | 5 | 3.8% |
| RETURN_CONTRACT_CHANGE | 5 | 3.8% |
| PROC_SYS_OUTPUT_CHANGE | 3 | 2.3% |
| IOCTL_NETLINK_ABI_CHANGE | 1 | 0.8% |
| SYSCALL_SEMANTIC_CHANGE | 1 | 0.8% |

## Negative kinds

Imported `TEST_ONLY` and `DOCUMENTATION_ONLY` values are preserved as legacy metadata but normalized to `TEST_DOC_COMMENT_ONLY` here.

| Kind | Count | Share of Negative |
|---|---:|---:|
| TEST_DOC_COMMENT_ONLY | 60 | 69.0% |
| BEHAVIOR_PRESERVING_REFACTOR | 9 | 10.3% |
| PROFILE_BOUNDARY_FALSE_POSITIVE | 7 | 8.0% |
| INTERNAL_ONLY | 6 | 6.9% |
| BUGFIX_WITHIN_CONTRACT | 3 | 3.4% |
| UNREACHABLE_OR_DISABLED | 2 | 2.3% |

## N/F view

Negative cases: **87**. Strict profile-boundary false-positive cases (`PROFILE_BOUNDARY_FALSE_POSITIVE`): **7**.

F IDs: `PCAT-N023`, `PCAT-N027`, `PCAT-N035`, `PCAT-N039`, `PCAT-N052`, `PCAT-N057`, `PCAT-N082`
