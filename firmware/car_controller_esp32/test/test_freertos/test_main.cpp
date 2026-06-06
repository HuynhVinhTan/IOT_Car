#include <Arduino.h>
#include <unity.h>

// Các biến giả lập môi trường của CarController
SemaphoreHandle_t testMutex;
QueueHandle_t testQueue;
int sharedDriveModeState = 0;

void setUp(void) {
    testMutex = xSemaphoreCreateMutex();
    testQueue = xQueueCreate(10, sizeof(char*));
    sharedDriveModeState = 0;
}

void tearDown(void) {
    vSemaphoreDelete(testMutex);
    vQueueDelete(testQueue);
}

void test_telemetry_queue_communication(void) {
    // 1. Giả lập Task phần cứng liên tục đẩy Telemetry JSON vào Queue
    const char* messages[] = {"{\"mode\":\"IDLE\"}", "{\"speed\":10}", "{\"obstacle\":true}"};
    for (int i = 0; i < 3; i++) {
        char* msg = strdup(messages[i]);
        BaseType_t res = xQueueSend(testQueue, &msg, 0); // Không bao giờ block
        TEST_ASSERT_EQUAL(pdPASS, res);
    }

    // Kiểm tra Queue có chứa đúng 3 tin nhắn không
    TEST_ASSERT_EQUAL(3, uxQueueMessagesWaiting(testQueue));

    // 2. Giả lập Task mạng (Network Task) từ từ lấy tin nhắn ra gửi đi
    for (int i = 0; i < 3; i++) {
        char* receivedMsg = nullptr;
        BaseType_t res = xQueueReceive(testQueue, &receivedMsg, 0);
        TEST_ASSERT_EQUAL(pdTRUE, res);
        TEST_ASSERT_EQUAL_STRING(messages[i], receivedMsg);
        free(receivedMsg); // Phải giải phóng bộ nhớ
    }
}

// Task phụ để giả lập việc ghi dữ liệu của WebSocket
void test_network_command_task(void* parameter) {
    for (int i = 0; i < 100; i++) {
        xSemaphoreTake(testMutex, portMAX_DELAY);
        sharedDriveModeState++; // Mô phỏng đổi trạng thái xe
        xSemaphoreGive(testMutex);
        vTaskDelay(pdMS_TO_TICKS(1));
    }
    vTaskDelete(NULL);
}

void test_mutex_locking_mechanism(void) {
    // Khởi tạo 2 Task mạng cùng lúc cố tình cập nhật trạng thái xe
    xTaskCreatePinnedToCore(test_network_command_task, "NetworkTask1", 2048, NULL, 5, NULL, 1);
    xTaskCreatePinnedToCore(test_network_command_task, "NetworkTask2", 2048, NULL, 5, NULL, 1);
    
    // Đợi 200ms cho các Task chạy xong
    vTaskDelay(pdMS_TO_TICKS(200));
    
    // Nếu Mutex hoạt động đúng (không bị Race Condition ghi đè biến), tổng số lần đổi trạng thái phải là 200
    TEST_ASSERT_EQUAL(200, sharedDriveModeState);
}

void setup() {
    delay(2000); // Đợi cổng Serial ổn định
    UNITY_BEGIN();
    RUN_TEST(test_telemetry_queue_communication);
    RUN_TEST(test_mutex_locking_mechanism);
    UNITY_END();
}

void loop() {
    // Kết thúc test, vòng lặp ngủ vĩnh viễn
    vTaskDelay(portMAX_DELAY);
}
