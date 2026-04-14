CHAT_PAGE_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Assistant Chat</title>
  <style>
    :root { color-scheme: dark; }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, system-ui, sans-serif;
      background: #111317;
      color: #f3f5f7;
    }
    .app {
      display: grid;
      grid-template-columns: minmax(0, 1.7fr) minmax(320px, 1fr);
      min-height: 100vh;
    }
    .panel {
      padding: 24px;
      border-right: 1px solid #252a33;
    }
    .panel:last-child {
      border-right: 0;
      background: #161a20;
    }
    h1, h2 { margin: 0 0 16px; font-size: 20px; }
    .meta, .controls {
      display: grid;
      gap: 12px;
      margin-bottom: 16px;
    }
    .row {
      display: grid;
      gap: 12px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    label {
      display: grid;
      gap: 6px;
      font-size: 13px;
      color: #c2c8d0;
    }
    input, select, textarea, button, pre {
      font: inherit;
    }
    input, select, textarea {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #313846;
      border-radius: 8px;
      background: #0e1116;
      color: #f3f5f7;
    }
    textarea {
      min-height: 120px;
      resize: vertical;
    }
    button {
      border: 0;
      border-radius: 8px;
      background: #4f8cff;
      color: #fff;
      padding: 10px 14px;
      cursor: pointer;
    }
    button.secondary {
      background: #252a33;
    }
    .messages {
      display: grid;
      gap: 12px;
      margin-top: 20px;
    }
    .message {
      padding: 14px;
      border: 1px solid #252a33;
      border-radius: 8px;
      background: #161a20;
      white-space: pre-wrap;
      line-height: 1.5;
    }
    .message.user {
      background: #12243f;
    }
    .debug-block {
      margin-top: 16px;
    }
    .prompt-messages {
      display: grid;
      gap: 12px;
    }
    .prompt-message {
      border: 1px solid #252a33;
      border-radius: 8px;
      background: #0e1116;
      overflow: hidden;
    }
    .prompt-message summary {
      list-style: none;
      cursor: pointer;
      padding: 12px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border-bottom: 1px solid #252a33;
    }
    .prompt-message summary::-webkit-details-marker {
      display: none;
    }
    .prompt-role {
      font-size: 12px;
      color: #9aa4b2;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .prompt-preview {
      flex: 1;
      min-width: 0;
      color: #cfd6df;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-size: 13px;
    }
    .prompt-content {
      margin: 0;
      padding: 14px;
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.6;
      max-height: 320px;
      overflow: auto;
    }
    pre {
      margin: 0;
      padding: 14px;
      border: 1px solid #252a33;
      border-radius: 8px;
      background: #0e1116;
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.5;
      max-height: 320px;
      overflow: auto;
    }
    .status {
      font-size: 13px;
      color: #9aa4b2;
      margin-top: 8px;
    }
  </style>
</head>
<body>
  <div class="app">
    <section class="panel">
      <h1>AI Assistant Chat</h1>
      <div class="controls">
        <div class="row">
          <label>user_id
            <input id="userId" value="u-primary" />
          </label>
          <label>stage override
            <input id="stage" list="stageOptions" placeholder="留空则按 user_id 解析" />
            <datalist id="stageOptions">
              <option value="primary_school"></option>
              <option value="junior_high_school"></option>
              <option value="senior_high_school"></option>
              <option value="cet"></option>
              <option value="ielts"></option>
              <option value="toefl"></option>
              <option value="postgraduate_exam"></option>
            </datalist>
          </label>
        </div>
        <div class="row">
          <label>provider
            <select id="provider">
              <option value="kimi" selected>kimi</option>
              <option value="openai">openai</option>
              <option value="dashscope">dashscope</option>
            </select>
          </label>
          <label>model
            <select id="model"></select>
          </label>
        </div>
        <label>message
          <textarea id="message">我写的是 I go to library yesterday. 这样翻对吗？请帮我改一下并解释。</textarea>
        </label>
        <div class="row">
          <button id="sendBtn">发送</button>
          <button id="clearBtn" class="secondary" type="button">清空消息</button>
        </div>
      </div>
      <div id="status" class="status">就绪</div>
      <div id="messages" class="messages"></div>
    </section>
    <aside class="panel">
      <h2>Debug</h2>
      <div class="debug-block">
        <label>Usage</label>
        <div class="status">Prompt Tokens / Completion Tokens / Total Tokens / Cached Tokens</div>
        <pre id="usageMeta">等待请求...</pre>
      </div>
      <div class="debug-block">
        <label>Resolved Context</label>
        <pre id="resolvedMeta">等待请求...</pre>
      </div>
      <div class="debug-block">
        <label>System Prompt</label>
        <pre id="systemPrompt">等待请求...</pre>
      </div>
      <div class="debug-block">
        <label>Full Prompt Messages</label>
        <div id="promptMessages" class="prompt-messages">
          <pre id="fullPrompt">等待请求...</pre>
        </div>
      </div>
      <div class="debug-block">
        <label>Raw Response JSON</label>
        <pre id="rawJson">等待请求...</pre>
      </div>
    </aside>
  </div>
  <script>
    const messagesEl = document.getElementById('messages');
    const statusEl = document.getElementById('status');
    const rawJsonEl = document.getElementById('rawJson');
    const usageMetaEl = document.getElementById('usageMeta');
    const systemPromptEl = document.getElementById('systemPrompt');
    const fullPromptEl = document.getElementById('fullPrompt');
    const promptMessagesEl = document.getElementById('promptMessages');
    const resolvedMetaEl = document.getElementById('resolvedMeta');
    const inputEls = {
      userId: document.getElementById('userId'),
      stage: document.getElementById('stage'),
      provider: document.getElementById('provider'),
      model: document.getElementById('model'),
      message: document.getElementById('message'),
    };
    const providerModels = {
      kimi: ['moonshot-v1-8k'],
      openai: ['gpt-5-mini'],
      dashscope: ['qwen-plus'],
    };

    function addMessage(role, content) {
      const node = document.createElement('div');
      node.className = `message ${role}`;
      node.textContent = content;
      messagesEl.appendChild(node);
    }

    function createPromptMessageNode(message, index) {
      const details = document.createElement('details');
      details.className = 'prompt-message';
      if (index === 0) {
        details.open = true;
      }

      const summary = document.createElement('summary');
      const role = document.createElement('span');
      role.className = 'prompt-role';
      role.textContent = message.role;
      const preview = document.createElement('span');
      preview.className = 'prompt-preview';
      preview.textContent = message.content.replace(/\\s+/g, ' ').trim() || '(empty)';
      summary.appendChild(role);
      summary.appendChild(preview);

      const content = document.createElement('pre');
      content.className = 'prompt-content';
      content.textContent = message.content;

      details.appendChild(summary);
      details.appendChild(content);
      return details;
    }

    function renderPromptMessages(messages) {
      promptMessagesEl.innerHTML = '';
      if (!messages || messages.length === 0) {
        fullPromptEl.textContent = '等待请求...';
        promptMessagesEl.appendChild(fullPromptEl);
        return;
      }
      messages.forEach((message, index) => {
        promptMessagesEl.appendChild(createPromptMessageNode(message, index));
      });
    }

    function syncModelOptions() {
      const provider = inputEls.provider.value;
      const models = providerModels[provider] || [];
      const currentValue = inputEls.model.value;
      inputEls.model.innerHTML = '';
      models.forEach((model) => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        inputEls.model.appendChild(option);
      });
      if (models.includes(currentValue)) {
        inputEls.model.value = currentValue;
      } else if (models.length > 0) {
        inputEls.model.value = models[0];
      }
    }

    inputEls.provider.addEventListener('change', syncModelOptions);
    syncModelOptions();

    document.getElementById('clearBtn').addEventListener('click', () => {
      messagesEl.innerHTML = '';
      rawJsonEl.textContent = '等待请求...';
      usageMetaEl.textContent = '等待请求...';
      systemPromptEl.textContent = '等待请求...';
      renderPromptMessages([]);
      resolvedMetaEl.textContent = '等待请求...';
      statusEl.textContent = '已清空';
    });

    document.getElementById('sendBtn').addEventListener('click', async () => {
      const payload = {
        message: inputEls.message.value,
        conversation_id: 'chat-debug',
        user_id: inputEls.userId.value || null,
        stage: inputEls.stage.value || null,
        provider: inputEls.provider.value || null,
        model: inputEls.model.value || null,
      };
      statusEl.textContent = '请求中...';
      addMessage('user', payload.message);
      try {
        const response = await fetch('/assistant/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await response.json();
        rawJsonEl.textContent = JSON.stringify(data, null, 2);
        if (!response.ok) {
          addMessage('assistant', `请求失败: ${data.detail || response.status}`);
          statusEl.textContent = '请求失败';
          return;
        }
        addMessage('assistant', data.reply);
        systemPromptEl.textContent = data.debug.system_prompt;
        renderPromptMessages(data.debug.request_messages);
        usageMetaEl.textContent = JSON.stringify({
          prompt_tokens: data.usage.prompt_tokens,
          completion_tokens: data.usage.completion_tokens,
          total_tokens: data.usage.total_tokens,
          cached_tokens: data.usage.cached_tokens,
          cache_hit_ratio: data.usage.cache_hit_ratio,
        }, null, 2);
        resolvedMetaEl.textContent = JSON.stringify({
          user_id: payload.user_id,
          stage_override: payload.stage,
          resolved_stage: data.debug.resolved_stage,
          stage_source: data.debug.stage_source,
          loaded_skills: data.debug.loaded_skills,
          loaded_stage_context: data.debug.loaded_stage_context,
          history_messages_loaded: data.debug.history_messages_loaded,
          history_messages_trimmed: data.debug.history_messages_trimmed,
          context_window_tokens: data.debug.context_window_tokens,
          input_budget_tokens: data.debug.input_budget_tokens,
          estimated_input_tokens: data.debug.estimated_input_tokens,
          provider: data.provider,
          model: data.model,
        }, null, 2);
        statusEl.textContent = '请求完成';
      } catch (error) {
        addMessage('assistant', `请求失败: ${error}`);
        statusEl.textContent = '请求失败';
      }
    });
  </script>
</body>
</html>
"""
