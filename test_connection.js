// 测试前端到后端的连接
const axios = require('axios');

async function testConnection() {
  try {
    console.log('测试后端健康检查...');
    const response = await axios.get('http://localhost:8080/api/health');
    console.log('✅ 后端健康检查成功:', response.data);
    
    console.log('\n测试每日限制状态...');
    const limitResponse = await axios.get('http://localhost:8080/api/daily-limit/status');
    console.log('✅ 每日限制状态:', limitResponse.data);
    
    console.log('\n测试房间创建...');
    const roomResponse = await axios.post('http://localhost:8080/api/room/create', {
      question: '测试连接'
    });
    console.log('✅ 房间创建成功:', roomResponse.data.thread_id);
    
  } catch (error) {
    console.error('❌ 连接测试失败:', error.message);
    if (error.response) {
      console.error('响应状态:', error.response.status);
      console.error('响应数据:', error.response.data);
    }
  }
}

testConnection();
