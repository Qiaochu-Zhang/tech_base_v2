# 前沿技术情报与预警平台 - 开发任务板

> 规则：
> 1. 每次只允许完成一个 Block。
> 2. 未被标记为 [x] 的 Block 才可执行。
> 3. 不得修改已完成 Block 的功能，除非修复明确 bug。
> 4. 所有变更必须符合 spec.md 数据模型与字段命名。
> 5. 每个 Block 完成后必须输出：
>    - 变更文件列表
>    - 核心逻辑说明
>    - 本地验证步骤

---

# 当前阶段：V1.5 前端样机完善

---

## [x] Block 1 - localStorage 闭环跑通

### 目标
跑通完整流程：

上传 → AI建议 → 人工修正 → 发布 → 总表展示（基于 localStorage）

### 范围
- 不引入后端
- 不引入数据库
- 不修改字段结构
- 不大规模改 UI
- 允许补充趋势图面板 X/Y 轴名称与分度值（index.html）

### 要求
- 发布后写入 localStorage
- 状态从 draft → ai_suggested → published
- 总表页面读取 published 状态数据
- published 数据参与筛选

### 验收标准
- 刷新页面数据仍在（localStorage 持久）
- draft 数据不出现在总表
- published 才参与筛选
- 不报 console error

---

## [x] Block 2 - 指标抽取规则模块化

### 目标
实现 spec.md 中定义的规则抽取逻辑，并封装为独立模块

### 规则
1. 匹配正文中的数字（支持整数/小数/百分号）
2. 检查数字前10个字符是否包含 indicator_defs.name
3. 若多个匹配，选择距离最近的
4. 生成结构：

{
  name,
  suggested_value,
  unit_default,
  confidence,
  evidence
}

### 要求
- 抽取逻辑放在独立文件（如 /lib/extractor.js）
- 页面只调用函数，不写复杂逻辑
- 不自动写入数据库
- 用户必须手动确认

### 验收标准
- 点击“提交并生成AI建议”能生成建议
- 多个指标时选最近
- 无匹配时返回空数组
- 不影响现有页面结构

---

## [x] Block 3 - 发布校验与预警规则强化

### 目标
实现发布前强校验逻辑

### 规则
发布时必须满足：

- title 非空
- content 非空
- 至少一个 domain
- 若开启预警：
    - alert_title 必填
    - alert_body 必填
    - reviewer_comment 必填

### 要求
- 封装为统一校验函数
- 不允许绕过校验发布
- 错误提示清晰

### 验收标准
- 缺少字段无法发布
- 关闭预警不需要填写 alert 字段
- 不影响 draft 保存

---

## [x] Bugfix Block - 详情页/工作台/领域树交互修复

### 目标
仅修复 bug + 小交互增强（不做 UI 重构）：

- 详情页支持从 localStorage drafts / published_items 查找
- dashboard 分级汇总表下钻过滤修复
- 左侧领域树路径展开与高亮

### 要求
- 不改变现有 UI 结构
- 保持现有数据结构与字段命名
- 只做最小必要改动

### 验收标准
- 详情页可打开本地草稿与本地发布条目
- 分级汇总表点击数字后只显示命中的条目
- 下钻后仅展开当前路径并高亮当前节点

---

## [ ] Block 4 - 总表合并与筛选稳定化

### 目标
实现 data/*.json + localStorage 合并读取

### 要求
- published 数据统一进入同一数组
- 支持：
    - domain 筛选
    - 时间筛选
    - source_types
    - info_types
    - 是否有预警
    - 是否有 comment
- 所有筛选基于 published

### 验收标准
- 筛选组合不会报错
- 筛选结果稳定
- 不影响页面性能

---

# V1.6 - 后端与数据库落地

---

## [ ] Block 5 - FastAPI 后端骨架

### 目标
创建最小可运行后端

### 要求
- FastAPI 项目结构
- /api/health
- 基础 info-items CRUD
- docker-compose 支持

### 验收标准
- docker compose up 成功
- /api/health 返回 200
- pytest 通过

---

## [ ] Block 6 - PostgreSQL 接入

### 目标
实现真实数据库存储

### 要求
- 建立 models
- 建立 migrations
- 连接 PostgreSQL
- 发布写入数据库
- 总表读取数据库

### 验收标准
- 发布数据进入数据库
- 重启容器数据仍在
- localStorage 不再使用

---

# 执行顺序

Block 必须按顺序执行：

1 → 2 → 3 → Bugfix → 4 → 5 → 6

user可以再中间任何时刻增加block

---

# Agent 执行指令模板

当执行时必须：

- 只完成当前未打勾的 Block
- 不修改其他 Block
- 小步提交（1-3 commit）

- 所有测试通过后才声明完成

