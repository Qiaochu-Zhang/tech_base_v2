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

## [x] Bugfix Block - 根目录选择实时高亮与趋势图更新

### 目标
修复根目录切换后需手动刷新才能更新高亮与趋势图的问题。

### 要求
- 根目录切换后立即刷新树高亮
- 趋势图面板自动使用当前领域范围
- 最小改动，不重构 UI

### 验收标准
- 切换根目录后高亮即时变化
- 趋势图无需手动刷新即更新

---

## [x] Block 4 - 总表合并与筛选稳定化

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

## [x] Bugfix Block - 上传复核预警生效与颜色选择

### 目标
修复上传&复核页强制开启预警后发布未生效的问题，并补充预警颜色选择。

### 要求
- 强制开启预警后发布需写入预警数据
- 发布时记录预警颜色
- 不改变现有 UI 结构，只做最小必要改动

### 验收标准
- 上传&复核页点击“强制开启预警”，发布后在详情页显示预警
- 预警颜色可选且在详情页展示一致

---

## [x] PageChange Block - 详情页布局与修订稿回流

### 目标
按页面改版要求调整详情页、总表、上传复核页交互：

- 详情页正文上移，详细信息下移
- 删除详情页快速跳转块
- 创建修订稿按钮移到顶部操作区并回流到上传&复核
- 总表增加删除情报按钮
- 上传页支持上传者调整密级

### 范围
- info_detail.html
- info_table.html
- upload_review.html

### 验收标准
- 详情页显示顺序为：标题信息 → 正文 → 指标 → 详细信息
- 详情页右侧不再显示快速跳转块
- 点击“创建修订稿”可带原始信息进入上传&复核页编辑
- 修订稿发布会生成新的情报 ID，不覆盖原情报
- 情报总表“新增/编辑预警”旁边有“删除情报”按钮
- 上传&复核页可编辑并保存 `classification`（密级）

---

# V1.6 - 后端与数据库落地

---

## [x] Block 5 - FastAPI 后端骨架

### 目标
创建最小可运行后端框架，为后续数据库接入做准备。

### 要求
- 建立标准 FastAPI 项目结构（如 app/main.py、routers、schemas 等）
- 实现 GET /api/health 接口，返回 { "status": "ok" }
- 实现 GET /api/domains/tree 接口（暂时从现有 data/domains.json 读取）
- 实现 GET /api/info-items 接口（暂时从 data/*.json 或 mock 数据返回，不做复杂筛选）
- 提供 docker-compose 支持（仅包含 api 服务，不接数据库）
- 提供最基本的 pytest 用例（至少包含 health 接口测试）

### 验收标准
- docker compose up -d --build 成功
- 访问 http://localhost:8000/api/health 返回 200
- /api/domains/tree 返回 JSON 数据
- pytest 通过

---

## [x] Block 6 - PostgreSQL 接入

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


