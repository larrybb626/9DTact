# AGENTS.md

## 项目概览
- `9DTact` 由两条主流水线组成：**3D 触觉形状重建** 与 **6D 力估计**；通过 ROS 脚本进行实时联动演示。
- 核心 Python 包为 `shape_reconstruction`、`force_estimation`、`data`、`model`（在 `setup.py` 中声明）。
- 仓库中原本没有现成的 Agent 规则文件；以下约定来自 `README.md` 与源码行为。

## 架构与数据流
- 相机路径：`shape_reconstruction/camera.py` 采集原始帧，应用已保存的矫正索引（`row_index.npy`、`col_index.npy`），再按配置裁剪。
- 形状路径：`shape_reconstruction/sensor.py` 将灰度图相对参考图的差分转换为 `height_map` 与点云梯度。
- 力路径：`force_estimation/estimator.py` 接收 3 通道形变表征图并预测归一化 6D wrench。
- 非 ROS 端到端示例是 `force_estimation/_1_Force_Estimation.py`（Sensor -> representation -> Estimator -> visualizer）。
- ROS 分工明确：发布节点在 `shape-force_ros/_1_Sensor_ros.py`，力推理节点在 `shape-force_ros/_3_Force_Estimation_ros.py`，融合可视化在 `shape-force_ros/_4_Shape_Force_ros.py`。

## 标准工作流（按现有实现）
- 标定结果是文件驱动且为形状重建必需：先运行 `shape_reconstruction/_1_Camera_Calibration.py`，再运行 `_2_Sensor_Calibration.py`，在 `shape_reconstruction/calibration/sensor_<id>/...` 下生成 `.npy` 产物。
- 形状重建运行：`shape_reconstruction/_3_Shape_Reconstruction.py` 读取 `shape_config.yaml`，依赖在线相机与已保存标定数组。
- 数据采集依赖 ROS + BOTA：`data_collection/collect_data.py` 订阅 `/rectify_crop_image` 与 wrench 话题，并写入 `../Dataset/{image,mixed_image,wrench}/<object_id>/`。
- 数据预处理是脚本流程（非库 API）：先 `wrench_normalization.py`，再 `split_train_test.py`（可选再跑 `split_train_test(objects).py`）。
- 训练/推理入口为 `force_estimation/train.py`；同一类通过 `train_mode` 切换训练与测试行为。

## 项目特有约定
- 配置以 YAML 为主且大量使用相对路径；脚本默认从各自目录启动（如 `open("shape_config.yaml")`、`../Dataset`）。
- 多个模块通过 `sys.path.append(... + '/../')` 追加仓库根目录；除非整体重构入口脚本，否则保持该风格。
- wrench 标签按轴归一化到 `[0,1]`，且范围在多个文件中硬编码（`train.py`、`wrench_normalization.py`、`collect_data.py`）；修改时需保持同步。
- 表征图通道约定为 BGR 风格（`Sensor.raw_image_2_representation`）：通道 0=参考灰度，1=变亮差分，2=变暗差分。
- `Estimator` 中刻意将单样本复制为 batch size=2（`estimator.py`），用于规避已记录的 PyTorch 单 batch 异常问题。

## 需要保持的集成契约
- 组件间 ROS 话题：`/rectify_crop_ref_image`、`/rectify_crop_image`、`/deformation_representation`、`/predicted_wrench`。
- 消息类型：图像话题使用 `sensor_msgs/Image`；力话题使用 `geometry_msgs/WrenchStamped`。
- `shape-force_ros/_1_Sensor_ros.py` 以 `latch=True` 发布参考图；下游节点依赖该行为（`wait_for_message`）。
- `data/DTactDataset` 读取的是保存“文件路径”的 `.npy` 数组，再惰性读取图像/wrench；数据划分脚本必须维持该契约。

## 安全改动建议（给 Agent）
- 若修改图像几何（`crop_size`、相机标定逻辑），需同时审查形状重建与力数据生成两条路径。
- 若修改 wrench 范围或归一化方式，需更新所有重复定义并重新生成归一化标签/数据划分文件。
- 若修改 ROS 话题名或消息结构，需同步更新所有 `shape-force_ros/*.py` 与 `data_collection/collect_data.py`。
- 若修改模型结构，输出维度应保持为 6；除非你也同步调整可视化、日志与 ROS wrench 发布代码。
- 优先按 `README.md` 的脚本级流程做冒烟验证；本仓库以“工作流可运行”优先，而非单元测试优先。

