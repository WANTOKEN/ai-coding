import json
import time
import requests
from django.http import StreamingHttpResponse

from bsdesign.utils.design_generator import DesignGenerator
from mod_manage.utils.views import BetaView


class ChatStreamView(BetaView):
    OLLAMA_BASE_URL = "http://localhost:11434"
    DEFAULT_MODEL = "qwen2.5-coder:3b"

    def post(self, request):
        try:
            # 解析请求参数
            if request.content_type == 'application/json':
                req_data = json.loads(request.body)
            else:
                req_data = request.POST.dict()

            user_message = req_data.get("message", "").strip()
            temperature = float(req_data.get("temperature", 0.8))
            model_name = req_data.get("model", self.DEFAULT_MODEL)
            max_tokens = int(req_data.get("max_tokens", 4096))
            system_prompt = req_data.get("system_prompt", "")

            if not user_message:
                return self._error_response("消息不能为空")

            stream_chat = self._stream_chat(user_message, system_prompt, temperature, model_name, max_tokens)
            return StreamingHttpResponse(
                stream_chat,
                content_type='text/event-stream; charset=utf-8'
            )

        except Exception as e:
            return self._error_response(f"请求处理错误: {str(e)}")

    def _error_response(self, message):
        data = {'type': 'error', 'message': message}
        content = f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        return StreamingHttpResponse(iter([content]), content_type='text/event-stream; charset=utf-8')

    def _send_data(self, data):
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    def _stream_chat(self, user_message, system_prompt, temperature, model_name, max_tokens):
        response = None
        chunk_count = 0
        response_text = ""
        generator = DesignGenerator(model_name=model_name)
        system_prompt = generator.get_prompt("stream")

        # 构建消息
        messages = []
        # if system_prompt:
        #     messages.append({"role": "system", "content": system_prompt})
        user_message += system_prompt
        messages.append({"role": "user", "content": user_message})

        start_time = time.time()

        try:
            # 开始信号
            yield self._send_data({'type': 'start', 'message': '开始生成回复...'})

            # 调用Ollama API
            response = requests.post(
                f'{self.OLLAMA_BASE_URL}/api/chat',
                json={
                    'model': model_name,
                    'messages': messages,
                    'stream': True,
                    'options': {
                        'temperature': temperature,
                        'num_predict': max_tokens,
                    }
                },
                stream=True,
                timeout=300
            )

            if response.status_code != 200:
                yield self._send_data({'type': 'error', 'message': f"API调用失败: {response.status_code}"})
                yield self._send_data({'type': 'end'})
                return

            # 缓存文本块 - 用于整行匹配
            buffered_chunk = ""
            usage_info = {}

            # 处理流式响应
            for line in response.iter_lines():
                if not line:
                    continue

                try:
                    chunk_data = json.loads(line.decode('utf-8'))

                    # 检查是否完成
                    if chunk_data.get('done', False):
                        # 发送最后的缓存文本（如果有）
                        if buffered_chunk:
                            chunk_count += 1
                            response_text += buffered_chunk
                            yield self._send_data({
                                'type': 'text',
                                'content': buffered_chunk,
                                'chunk_id': chunk_count
                            })

                        duration_ms = int((time.time() - start_time) * 1000)
                        usage_info = {
                            "prompt_tokens": chunk_data.get("prompt_eval_count", 0),
                            "completion_tokens": chunk_data.get("eval_count", 0),
                            "total_tokens": chunk_data.get("prompt_eval_count", 0) + chunk_data.get("eval_count", 0),
                        }

                        yield self._send_data({
                            'type': 'complete',
                            'message': '生成完成',
                            'usage': usage_info,
                            'duration_ms': duration_ms
                        })
                        break

                    # 提取消息内容
                    message = chunk_data.get('message', {})
                    content = message.get('content', '')

                    if content:
                        # 累积文本块到缓冲区
                        buffered_chunk += content

                        # 按换行符拆分处理完整行
                        lines = buffered_chunk.split('\n')

                        # 处理完整的行（除了最后一个可能不完整的部分）
                        while len(lines) > 1:
                            complete_line = lines.pop(0)
                            chunk_count += 1
                            response_text += complete_line + '\n'

                            # 发送完整行
                            yield self._send_data({
                                'type': 'text',
                                'content': complete_line + '\n',
                                'chunk_id': chunk_count
                            })

                        # 保留剩余的不完整行到缓冲区
                        buffered_chunk = lines[0] if lines else ""

                except json.JSONDecodeError:
                    continue
                except Exception:
                    continue

            # 处理最后可能残留的文本块
            if buffered_chunk:
                chunk_count += 1
                response_text += buffered_chunk
                yield self._send_data({
                    'type': 'text',
                    'content': buffered_chunk,
                    'chunk_id': chunk_count
                })

        except requests.exceptions.Timeout:
            yield self._send_data({'type': 'error', 'message': '请求超时'})
        except requests.exceptions.ConnectionError:
            yield self._send_data({'type': 'error', 'message': '无法连接到Ollama服务'})
        except Exception as e:
            yield self._send_data({'type': 'error', 'message': f'未知错误: {str(e)}'})

        finally:
            if response:
                try:
                    response.close()
                except:
                    pass
            yield self._send_data({'type': 'end'})
