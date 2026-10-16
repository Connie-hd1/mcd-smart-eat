# 麦省钱 · 今天吃啥 (mcd-smart-eat)

> 一个懂你预算的麦当劳点餐助手。不用算券，不用纠结，直接告诉你今天吃什么最划算。

## 😫 解决什么痛点？
每次想吃麦当劳，都要面对两个灵魂拷问：
1. **预算有限**：我只想花 20 块，怎么点才不会超支？
2. **选择困难**：菜单太多、优惠券太复杂，到底吃什么最划算？

**麦省钱** 就是为了解决这两个问题，让点餐回归简单。

## ✨ 核心功能
- 🎯 **预算硬约束**：输入你的预算（比如 15元/20元），直接淘汰超支选项。
- 🍔 **智能组合推荐**：结合麦当劳 MCP 的菜单、优惠券、门店数据，给出性价比最高的 1-3 个组合。
- 💰 **省了多少一目了然**：对比原价和到手价，告诉你这顿省了多少钱。
- 🍟 **口味与场景匹配**：不辣、想吃肉、想吃鸡块、还是只想随便吃点，它都能听懂。

## 🚀 如何使用
<img width="701" height="574" alt="1" src="https://github.com/user-attachments/assets/58b70d7d-c290-4483-99bc-0a68446768f3" />
<img width="691" height="598" alt="2" src="https://github.com/user-attachments/assets/8e070ea9-e4a9-4558-a61c-6c8a415d49e0" />
<img width="718" height="582" alt="3" src="https://github.com/user-attachments/assets/536ef803-634f-4337-ac88-58ffcf206ca1" />
<img width="683" height="578" alt="4" src="https://github.com/user-attachments/assets/28d83a21-f60a-44e1-8c9b-4067afc777fc" />
<img width="706" height="533" alt="5" src="https://github.com/user-attachments/assets/34b06653-b2fe-437e-8c42-d576df3cc3b0" />
<img width="696" height="510" alt="6" src="https://github.com/user-attachments/assets/0574cfea-e02c-43d6-a12d-3e947a0ee1b1" />

### 方式一：WorkBuddy 直接体验（推荐）
配置好 MCP 连接器后，直接发送指令：
> 预算20元，不吃辣，一个人吃，想要有主食有饮料，直接告诉我吃啥。

### 方式二：本地 Python 运行
1. 安装依赖：
   ```bash
   pip install -r requirements.txt

## 🛠️ 技术实现
- **开发工具**：WorkBuddy
- **数据连接**：麦当劳 MCP（使用了菜单、优惠券、门店等工具）
- **底层逻辑**：基于预算约束与评分规则进行组合推荐

## 📂 项目文件说明
- `README.md`：项目介绍
- `CONTEST_DECLARATION.md`：参赛声明
- `MCP_INTEGRATION.md`：MCP 工具调用说明
- `workbuddy.md`：WorkBuddy 开发对话上下文（用于比赛积分）

---
*本项目参与麦当劳中国程序员创意开发大赛*
