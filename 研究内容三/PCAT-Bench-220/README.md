# PCAT-Bench-220 数据集

本目录包含研究内容三测试使用的 PCAT-Bench-220 数据集。数据集通过人工筛选开源项目真实提交并结合代表性兼容性场景构造形成。

## 数据集规模

| 项目 | 数量 |
|---|---:|
| 用例总数 | 220 |
| 兼容性变化正例 | 133 |
| 无兼容性影响负例 | 87 |
| 软件仓库 | 18 |
| 正例兼容性变更类型 | 13 |
| 上游真实补丁 | 208 |
| 人工构造补丁 | 12 |

## 目录内容

```text
PCAT-Bench-220/
├── README.md
├── taxonomy.md
├── case_distribution.md
├── metrics_spec.md
└── items/
    ├── PCAT-P001/
    │   ├── meta.yaml
    │   └── patch.patch
    ├── ...
    └── PCAT-N087/
        ├── meta.yaml
        └── patch.patch
```

每个用例由两类必要文件构成：

- `meta.yaml`：用例标识、目标仓库、基线与补丁提交、变更文件/符号、兼容性类型和预期结果等元数据；
- `patch.patch`：待分析和测试的完整补丁。

## 配套文档

- `taxonomy.md`：13 类正例兼容性变化和负例类别定义；
- `case_distribution.md`：220 个用例的仓库、正负例和兼容性类型分布；

完整测试结论见上级目录的 `测试报告.md`。

