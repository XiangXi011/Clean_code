    -- SQL for creating all required database tables
    -- Please execute this entire script in your database client (like DBeaver).

    -- 1. 每日计划任务表 (Daily planned tasks table)
    CREATE TABLE IF NOT EXISTS daily_tasks (
        task_id INT AUTO_INCREMENT PRIMARY KEY,
        measure_date DATE NOT NULL,
        location_type VARCHAR(50) NOT NULL,
        point_name VARCHAR(100) NOT NULL,
        status VARCHAR(20) DEFAULT '待测量',
        INDEX (measure_date)
    ) COMMENT='每日计划任务表';

    -- 2. 固化炉主数据表 (Furnace master data table)
    CREATE TABLE IF NOT EXISTS furnaces (
        furnace_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE,
        last_measured DATE NULL
    ) COMMENT='固化炉主数据表';

    -- 3. 测量结果记录表 (Measurement results table)
    CREATE TABLE IF NOT EXISTS results (
        result_id INT AUTO_INCREMENT PRIMARY KEY,
        task_id INT NULL,
        furnace_id INT NULL,
        measure_time DATETIME NOT NULL,
        value_03 DECIMAL(10, 2) NOT NULL,
        value_05 DECIMAL(10, 2) NOT NULL,
        value_50 DECIMAL(10, 2) NOT NULL,
        operator VARCHAR(50) NULL,
        FOREIGN KEY (task_id) REFERENCES daily_tasks(task_id) ON DELETE SET NULL,
        FOREIGN KEY (furnace_id) REFERENCES furnaces(furnace_id) ON DELETE SET NULL
    ) COMMENT='所有测量的结果记录';

    ```

2.  **执行SQL脚本**
    * 打开 **DBeaver** 并连接到您的阿里云RDS数据库。
    * 打开刚刚创建的 `database_schema.sql` 文件，或者直接将文件中的所有SQL代码复制到一个新的SQL编辑器中。
    * **执行整个脚本**。在DBeaver中，这通常是通过点击工具栏中的“执行SQL脚本”按钮（一个带有绿色播放箭头的文档图标）来完成。
    

### **下一步**

当您成功执行完上述SQL脚本后，您的数据库中就已经创建好了所有需要的空表格。

现在，请回到您的终端，**再次运行每日计划生成脚本**：

```bash
python generate_daily_tasks.py
