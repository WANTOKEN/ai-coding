# 智能代码生成聊天工具

## 项目简介

这是一个基于 AI 的智能代码生成工具，集成了聊天对话和代码编辑功能，帮助开发者通过自然语言描述快速生成代码。

## 文件说明

| 文件 | 说明 |
|------|------|
| `ai.html` | 前端界面，包含聊天面板、代码编辑器、文件管理器等 UI 组件 |
| `chat_stream.py` | 后端视图，处理流式聊天请求，调用 Ollama API 生成响应 |

## 主要功能

### 前端 (ai.html)

- **智能对话** - 与 AI 助手对话，描述代码需求
- **代码生成** - 自动解析 AI 响应中的代码块并创建文件
- **代码编辑器** - 基于 ACE Editor 的在线编辑器，支持语法高亮
- **文件管理** - 多文件管理，支持新建、重命名、删除操作
- **实时预览** - HTML 文件实时预览和分屏视图
- **项目导出** - 将项目打包为 ZIP 文件下载
- **Markdown 渲染** - 支持 Markdown 格式显示和代码高亮

### 后端 (chat_stream.py)

- **流式响应** - 使用 Server-Sent Events (SSE) 实现实时流式输出
- **Ollama 集成** - 默认使用 `qwen2.5-coder:3b` 模型
- **自定义提示词** - 通过 `DesignGenerator` 获取系统提示词
- **错误处理** - 完善的超时和连接错误处理机制

## 技术栈

### 前端
- ACE Editor - 代码编辑器
- Highlight.js - 代码语法高亮
- Marked.js - Markdown 解析
- JSZip - 项目打包导出

### 后端
- Django - Web 框架
- Ollama API - 本地大模型服务
- StreamingHttpResponse - 流式响应

## 使用方法

1. 确保 Ollama 服务已启动 (`http://localhost:11434`)
2. 配置 API 地址（默认指向 Django 后端接口）
3. 在聊天框中描述代码需求，如"创建一个 Vue 组件"
4. AI 将生成代码并自动创建文件
5. 在编辑器中修改代码，使用预览功能查看效果
6. 导出项目为 ZIP 文件

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + Enter` | 发送消息 |
| `Ctrl + S` | 保存当前文件 |

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama 服务地址 |
| `DEFAULT_MODEL` | `qwen2.5-coder:3b` | 默认使用的模型 |
| `temperature` | `0.8` | 生成温度 |
| `max_tokens` | `4096` | 最大生成 token 数 |

## 依赖

```python
# Python 依赖
django
requests
```

## 注意事项

- 需要本地运行 Ollama 服务
- 支持多种编程语言的语法高亮
- API 地址会保存在 localStorage 中

<img width="1303" height="678" alt="image" src="https://github.com/user-attachments/assets/555e2590-b832-458d-9664-f3c027807799" />
