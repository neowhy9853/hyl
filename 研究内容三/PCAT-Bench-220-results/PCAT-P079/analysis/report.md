# PCA 兼容性变更分析报告

**仓库**: /home/soong/pca_benchmark/_repos/openldap
**基线**: e538a0c6b3 (ITS#10416 libldap: allow fractional seconds for timeouts in ldaprc)
**补丁**: 1780b21 (ITS#9022 Introduce -o remove-sids= to slapadd)
**Profile**: openldap

## 概要

| 指标 | 数量 |
|------|------|
| 变更文件 | 3 |
| 候选变更 | 8 |
| 兼容性变更 | 1 |
| 高优先级测试 | 0 |
| 中优先级测试 | 0 |
| 低优先级测试 | 1 |

---

## PCA-0001: 新 CLI 选项 remove-sids (CONFIG_CLI_BEHAVIOR_CHANGE)

- **测试优先级**: LOW
- **置信度**: 0.9
- **影响接口**: slapadd -o remove-sids=
- **旧代码位置**: servers/slapd/slapcommon.c:255-260
- **新代码位置**: servers/slapd/slapcommon.c:255-286
- **类型**: CONFIG_CLI_BEHAVIOR_CHANGE

### 变更前行为
slapadd 的 `-o` 选项解析器不识别 `remove-sids`。未识别的选项导致 parse_slapopt() 立即返回 -1。

### 变更后行为
slapadd 的 `-o` 选项解析器新增识别 `remove-sids=<sid>[,<sid>,...]`。解析逗号分隔的 SID 值，验证每个 SID (0..4095)，存入 sids_to_remove[]，设置 update_ctxcsn=1。如果指定的 SID 与 `-S` 配置的 serverID 冲突，slapadd 输出错误并退出。无效 SID 值输出错误并返回 -1。其他工具 (slapcat, slapindex) 收到调试消息后继续。

### 兼容性影响
这是一个纯增量的、选择加入的 CLI 选项变更。当不使用该选项时，所有现有行为完全保留（sids_to_remove 零初始化，所有新条件分支均不激活）。不会破坏现有 slapadd 脚本。

### 证据
```c
} else if ( ( strncasecmp( optarg, "remove-sids", len ) == 0 ) ) {
    switch ( tool ) {
    case SLAPADD:
        {
            char *arg = strtok( p, "," );
            if ( !arg ) {
                Debug( LDAP_DEBUG_ANY, "remove-sids needs an argument.\n" );
                return -1;
            }
            do {
                unsigned int u;
                if ( lutil_atou( &u, arg ) || u > SLAP_SYNC_SID_MAX ) {
                    Debug( LDAP_DEBUG_ANY, "unable to parse remove-sids=\"%s\".\n", arg );
                    return -1;
                }
                sids_to_remove[u] = 1;
                update_ctxcsn = 1;
            } while ( (arg = strtok( NULL, "," )) );
        }
        break;
    default:
        Debug( LDAP_DEBUG_ANY, "remove-sids meaningless for tool.\n" );
        break;
    }
```

### 静态调用链
未启用

### 复核建议
无破坏性变更预期。验证不使用 `-o remove-sids=` 时 slapadd 行为与基线相同。

### 测试建议
1) 验证不使用新选项时 slapadd 输出与基线一致  
2) 验证新选项正确解析 SID 值并拒绝无效值  
3) 验证 CSN 替换功能  
4) 验证 contextCSN 排除已移除的 SID  

---

## 测试结果摘要

| 测试 | 结果 |
|------|------|
| BEFORE slapadd (基线，无选项) | PASS |
| AFTER slapadd (无选项，回归测试) | PASS |
| AFTER slapadd -o remove-sids=0 (冲突检测) | PASS |
| AFTER slapadd -o remove-sids=1 (有效 SID) | PASS |
| AFTER slapadd -o remove-sids=1,2,3 (逗号分隔) | PASS |
| AFTER slapadd -o remove-sids=9999 (超出最大) | PASS |
| AFTER slapadd -o remove-sids= (空参数) | PASS |
| AFTER slapadd -o remove-sids=foo (非数字) | PASS |

**产物位置**: /home/soong/pca_benchmark/_repos/openldap/pca-results/1780b2/
