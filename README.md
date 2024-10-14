# README(JobSubPub)

---

## 系統簡介

JobSubPub旨在自動化定時從職缺網站爬取職缺資料，並根據使用者的訂閱條件，通過MQTT推播服務，實時或定時向外部服務傳送通知。


## **技術棧**

---

- **程式語言**: Python、Node.js
- **資料庫**: PostgreSQL
- **其他**: Socket.IO、Mosquitto (MQTT)、Docker、Prometheus、Grafana

## **系統功能**

---

**1. 定時職缺爬取與更新**
- 爬蟲系統定時從多個職缺網站（104、1111）爬取資料，更新到資料庫中。
  
**2. 使用者訂閱推播服務**
- 使用者可訂閱特定公司或特定職缺來實時取得通知
- 使用者可用模糊的訂閱條件來讓系統定時推播通知

**3. 系統監控與日誌**
- 簡易指標監控系統運行狀態


## **系統架構圖**

---

![deploy-diagram](img/deploy-diagram.png)
- **爬蟲引擎**  
  - 使用 Python 編寫，定時爬取常見職缺網站的職缺資料並更新到資料庫中。
  
- **資料庫**  
  - 選用PostgreSQL儲存職缺資料和使用者的訂閱資訊。
  - 資料庫主要包含職缺表、訂閱表以及推播表，並利用 PostgreSQL 的 JSONB 和 trigger 特性實現動態欄位設計與推播通知。

- **應用伺服器**  
  - 使用 Node.js 編寫，分為 Job Service 和 Publish Service。
  - Job Service 處理職缺查詢和訂閱操作，
  - Publish Service 負責根據資料庫更新或定時條件推播消息。

- **外部服務與通知模組**  
  - 外部服務透過 RESTful API 與應用伺服器互動，並使用 Socket.IO 即時向使用者推送通知，實現訂閱內容的即時顯示。
  - 額外設置 https://github.com/YiHsinTseng/NotificationSystem

- **監控與日誌記錄**  
  - 系統的可觀測性由 Prometheus 與 Grafana 提供，設置簡易監控指標，確保系統穩定運行。

## **系統運行**

---

1. 克隆項目到本地：

    ```bash
    git clone https://github.com/YiHsinTseng/JobSubPub.git
    ```
2. 移動到 Docker 資料夾：

    ```bash
    cd Docker
    ```

2. 根據 .env.example 建立.env

    ```
    PORT=4000
    PUB_PORT=4010

    DB_HOST=postgres
    DB_PORT=5432
    DB_NAME=jobs
    DB_USER=test
    DB_PASSWORD=test

    MQTT_BROKER_URL=mqtt://mosquitto:1884
    CLIENT_PORT=http://localhost:5050
    PASSPORT_SECRET=YOUR_SECRET
    JWT_EXPIRES_IN=1d

    MQTT_TOPIC=notifications
    MQTT_JOB=job_id_channel
    MQTT_COMPANY=company_name_channel
    QOS_LEVEL=1
    PUBLISH_CRON_TIME='00 22 * * *'
    REDIS_URL='redis://my-redis:6379'
    ```

4. 執行 Docker 指令運行：

    ```bash
    docker-compose up --build
    ```

