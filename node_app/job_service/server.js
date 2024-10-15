const express = require('express');
const cors = require('cors');

const jobRoutes = require('./routes/jobs');
const subRoutes = require('./routes/subscriptions');

const apiErrorHandler = require('./middlewares/apiErrorHandler');

const { monitoringMiddleware, prometheusMetricsHandler } = require('./metrics'); // 引入你的 metrics 模組

// 初始化 Express 應用
const app = express();
app.use(express.json());

const CORS_WHITE_LIST = process.env.WHITE_LIST.split(',');

app.use(cors({ // 要注意不同網址問題不然會fetch失敗
  origin: CORS_WHITE_LIST,
}));

// 中間件來處理計時
app.use(monitoringMiddleware);

app.use('/api', jobRoutes);
app.use('/api', subRoutes);
app.use(apiErrorHandler);

// 添加一個 Prometheus 指標路由
app.get('/metrics', prometheusMetricsHandler);

// 啟動伺服器
const PORT = process.env.JOBS_PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
