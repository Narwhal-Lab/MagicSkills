# Skills-For-All-Agent-首个无缝支持所有agent框架的skill系统

与**Claude Code**的skills system完全吻合的实现-同时不仅仅局限于**Claude Code的skills system，它 更轻量化 更兼容 更自由化 更生态化**

## 这是什么

一个python package 作为skills系统去无缝接轨所有agent框架，并将skill内容和agent使用skill能力绑定形成一个完整skill生态

## 出发点

anthropic Claude提出了关于一新范式skills的相关规范来扩展大模型的功能 [Agent Skills ](https://code.claude.com/docs/en/skills)

但存在问题是我并没有寻找到anthropic Claude关于 模型是如何使用skills的代码实现。于是在阅读skills文档后，我决定自己实现一套skills系统来使得模型可以使用skills

期间我寻找了相关使用skill的实战与实现的资源

1. agentscope 的skill实现[Agent Skill](https://doc.agentscope.io/tutorial/task_agent_skill.html#integrating-agent-skills-with-reactagent)
2. anthropic sdk 的skill实战 [src/anthropic/resources/beta/skills](https://github.com/anthropics/anthropic-sdk-python/tree/main/src/anthropic/resources/beta/skills)
3. claude-codebooks的skill实战  [skills](https://github.com/anthropics/claude-cookbooks/tree/main/skills)
4. DeepAgents的 skill实现 [Using skills with Deep Agents](https://blog.langchain.com/using-skills-with-deep-agents/)
5. openskills的skill实现 [Universal skills loader for AI coding agents - npm i -g openskills](https://github.com/numman-ali/openskills)

## 存在的问题

但它们存在以下问题

1. 和agent框架高度耦合 并没有统一成一个一致的接口能面向所有agent框架使用
2. 部分skills的实现并没有开发源码
3. 关于各个skill文档内容 也并没有面向所有agent框架 也没有与skills实现深度绑定
4. 没有以一个统一的 轻量化的方式提供给所有agent框架
5. 冗余的不是python的外部软件生态 而大部分agent框架是由python完成的
6. 强制在system prompt给出所有skill描述。而不是模型自主地去考虑是否要查看所有skill描述并使用skill

## 想法

所以，我实现了一个skill系统，它能以非常简单的方式无缝提供给所有agent框架使用skill。同时各个skill文档内容也随着这个skill系统深度绑定，所有agent框架可以在使用skill的同时也能获取skill文档。

而要想实现上述。通过如下角度实现最为合适

1. python package 形式。几乎所有agent框架使用python。以包的形式提供skill能力和skill文档，能够让agent框架上手即用
2. 通过已有的所有agent框架的最通用的技术来实现这个skill能力。这样能保证所有agent框架都可以使用

## 优点

1. 无缝兼容所有agent框架
2. 建立在传统框架技术上
3. 只需要pip3 install skills_for_all_agent 并提供给agent一个tool即可让agent使用skill
4. 包中带有skill内容，所有通过pip3 install skills_for_all_agent后都可以通过自带的一个前端界面自动化生成自己想要的skill内容 或者上传自己的skill内容。
5. agent使用skill时可以自动使用你以及生成的skill内容或者你上传的skill内容
6. 不会强制在system prompt给它skill相关提示词。只用给它这个工具的描述。它便可以自主地决定是否要适用skills。

## 交流

如果有不足的地方想提供建议或者想一起参与的大佬。 请扫码加入微信群。欢迎大家一起交流！！！

![示例图片](image/f8a6f9fef45eedf1d6ba5adbbe03016a.jpg)
