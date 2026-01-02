<template>
    <div class="background">
    <HeaderTopAfterLogin :userId="userId" :role="role"></HeaderTopAfterLogin>
    <div style="position:absolute;top:120px">
        <!-- 创建的游戏列表 -->
        <!-- 消息显示区域 -->
        <div v-if="message" class="message-box" :class="messageType">
            {{ message }}
        </div>
        <div>
            <button @click="goBackToUserInfoPage" class="goBackToUserInfoPageButton">回到个人界面</button>
            <h1>我创建的游戏</h1>
            <ul v-if="createdGames.length > 0">
                <!-- 遍历显示已创建的游戏 -->
                <li v-for="game in createdGames" :key="game.game_id">
                    <strong>{{ game.game_name }}</strong> -
                    状态: {{ game.status }} -
                    玩家数: {{ game.current_players }}/{{ game.max_players }}
                    游戏id: {{ game.game_id }}
                    <!-- 删除游戏按钮 -->
                    <button @click="deleteGame(game.game_id)">删除游戏</button>
                    <!-- 管理游戏按钮 -->
                    <button @click="manageGame(game.game_id)">管理游戏</button>
                </li>
            </ul>
            <p v-else>您尚未创建任何游戏。</p>
        </div>

        <!-- 创建游戏表单 -->
        <div>
            <h1>创建游戏</h1>
            <div>
                <!-- 输入游戏名称 -->
                <label for="gameName">游戏名称:</label>
                <input id="gameName" v-model="inputGameName" type="text" placeholder="请输入游戏名称" required />
            </div>
            <div>
                <!-- 输入最大玩家数 -->
                <label for="maxPlayers">最大玩家数:</label>
                <input id="maxPlayers" v-model.number="inputMaxPlayers" type="number" placeholder="请输入最大玩家数" min="1"
                    required />
            </div>

            <!-- 常量 -->
            <div>
                <h2>常量</h2>
                <ul>
                    <!-- 遍历显示常量 -->
                    <li v-for="(constant, index) in constants" :key="index">
                        {{ constant.name }} - 初始值: {{ constant.initialValue }} - 展示: {{ constant.display ? '是' : '否'
                        }}
                    </li>
                </ul>
                <!-- 添加常量按钮 -->
                <button @click="showAddConstantModal = true">+</button>

                <!-- 添加常量模态框 -->
                <div v-if="showAddConstantModal" class="modal">
                    <div class="modal-content">
                        <h3>添加常量</h3>
                        <form @submit.prevent="addConstant">
                            <label>名称: <input v-model="newConstant.name" required /></label>
                            <label>初始值: <input v-model.number="newConstant.initialValue" type="number"
                                    required /></label>
                            <label>展示: <input type="checkbox" v-model="newConstant.display" /></label>
                            <div class="modal-actions">
                                <button type="submit">添加</button>
                                <button type="button" @click="cancelAddConstant">取消</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            <!-- 变量 -->
            <div>
                <h2>变量</h2>

                <!-- 环境变量 -->
                <h3>环境变量</h3>
                <ul>
                    <li v-for="(variable, index) in environmentVariables" :key="variable.id">
                        {{ variable.id }}: 名称: {{ variable.name }} - 初始值: {{ variable.initialValue }} - 操作符: {{
                            variable.operator }} - 操作数: {{ variable.operand }} - 每{{ variable.everyRound }}回合 - 展示: {{
                            variable.display ? '是' : '否' }}
                        <button @click="deleteEnvironmentVariable(index)">删除</button>
                    </li>
                </ul>

                <!-- 决策变量 -->
                <h3>决策变量</h3>
                <ul>
                    <li v-for="(variable, index) in decisionVariables" :key="variable.id">
                        <div v-if="variable.typeDetail === 'enum'">
                            {{ variable.id }}: 名称: {{ variable.name }} - 类型: {{ variable.typeDetail }} 枚举值: {{
                                variable.enumValues }}
                            <button @click="deleteDecisionVariable(index)">删除</button>
                        </div>
                        <div v-else-if="variable.typeDetail === 'number'">
                            {{ variable.id }}: 名称: {{ variable.name }} - 类型: {{ variable.typeDetail }}判断符: {{
                                variable.conditionOperator }} - 判断数: {{ variable.conditionValue }} - 数值类型: {{
                                variable.numberType === 'integer' ? '整数' : '小数' }}
                            <button @click="deleteDecisionVariable(index)">删除</button>
                        </div>
                    </li>
                </ul>

                <!-- 应变量 -->
                <h3>应变量</h3>
                <ul>
                    <li v-for="(variable, index) in dependentVariables" :key="variable.id">
                        {{ variable.id }}: 名称: {{ variable.name }} - 初始值: {{ variable.initialValue }} - 公式: {{
                            variable.formula }}
                        <button @click="deleteDependentVariable(index)">删除</button>
                    </li>
                </ul>
                <!-- 显示变量类型选择器 -->
                <button @click="showVariableTypeSelector = true">+</button>

                <!-- 变量类型选择器 -->
                <div v-if="showVariableTypeSelector">
                    <label for="variableType">选择变量类型:</label>
                    <select v-model="selectedVariableType" id="variableType">
                        <option value="环境变量">环境变量</option>
                        <option value="决策变量">决策变量</option>
                        <option value="应变量">应变量</option>
                    </select>
                    <button @click="confirmVariableType">确认</button>
                    <button @click="cancelAddVariable">取消</button>
                </div>

                <!-- 环境变量表单 -->
                <div v-if="selectedVariableType === '环境变量'">
                    <h3>添加环境变量</h3>
                    <form @submit.prevent="addEnvironmentVariable">
                        <label>名称: <input v-model="envVariable.name" required /></label>
                        <label>初始值: <input v-model.number="envVariable.initialValue" type="number" required /></label>
                        <label>操作符:
                            <input v-model="envVariable.operator" placeholder="如 +, -, *, /, %" required />
                            <small>合法操作符: +, -, *, /, %</small>
                        </label>
                        <label>操作数:
                            <select v-model="envVariable.operandType" required>
                                <option value="variable">选择变量</option>
                                <option value="number">固定数字</option>
                            </select>
                        </label>
                        <div v-if="envVariable.operandType === 'variable'">
                            <label>选择变量:
                                <select v-model="envVariable.operand" required>
                                    <option v-for="variable in allVariables" :key="variable.id" :value="variable.id">
                                        {{ variable.id }}: {{ variable.name }}
                                    </option>
                                </select>
                            </label>
                        </div>
                        <div v-if="envVariable.operandType === 'number'">
                            <label>输入数字: <input v-model.number="envVariable.operand" type="number" required /></label>
                        </div>
                        <label>每_回合: <input v-model.number="envVariable.everyRound" type="number" required /></label>
                        <label>展示: <input type="checkbox" v-model="envVariable.display" /></label>
                        <button type="submit">添加</button>
                    </form>
                </div>

                <!-- 决策变量表单 -->
                <div v-if="selectedVariableType === '决策变量'">
                    <h3>添加决策变量</h3>
                    <form @submit.prevent="addDecisionVariable">
                        <label>名称: <input v-model="decisionVariable.name" required /></label>
                        <label>类型:
                            <select v-model="decisionVariable.type" required>
                                <option value="enum">枚举型</option>
                                <option value="number">数值型</option>
                            </select>
                        </label>
                        <div v-if="decisionVariable.type === 'enum'">
                            <label>枚举值: <input v-model="decisionVariable.enumValues" placeholder="用逗号分隔"
                                    required /></label>
                        </div>
                        <div v-if="decisionVariable.type === 'number'">
                            <label>判断符: <input v-model="decisionVariable.conditionOperator" placeholder="如 <, >, ="
                                    required /></label>
                            <label>判断数: <input v-model="decisionVariable.conditionValue" type="number"
                                    required /></label>
                            <label>数值类型:
                                <select v-model="decisionVariable.numberType" required>
                                    <option value="integer">整数</option>
                                    <option value="float">小数</option>
                                </select>
                            </label>
                        </div>
                        <button type="submit">添加</button>
                    </form>
                </div>

                <!-- 应变量表单 -->
                <div v-if="selectedVariableType === '应变量'">
                    <h3>添加应变量</h3>
                    <form @submit.prevent="addDependentVariable">
                        <label>名称: <input v-model="dependentVariable.name" required /></label>
                        <label>初始值: <input v-model.number="dependentVariable.initialValue" type="number"
                                required /></label>
                        <label>公式: <input v-model="dependentVariable.formula"
                                placeholder="请输入公式，以=开头,其中的引用需要使用索引，如=d1+d2" required /></label>
                        <button type="submit">添加</button>
                    </form>
                </div>

                <!-- 目标变量 -->
                <div>
                    <h2>目标变量</h2>
                    <form @submit.prevent="setTargetVariable">
                        <label for="targetVariable">选择目标变量:</label>
                        <select v-model="targetVariable" id="targetVariable" required>
                            <option v-for="variable in dependentVariables" :key="variable.id" :value="variable.id">
                                {{ variable.id }}: {{ variable.name }}
                            </option>
                        </select>
                        <label>
                            <input type="radio" value="asc" v-model="targetOrder" /> 顺序
                        </label>
                        <label>
                            <input type="radio" value="desc" v-model="targetOrder" /> 逆序
                        </label>
                        <button type="submit">设置目标变量</button>
                    </form>
                </div>
            </div>
            <!-- 提交创建游戏 -->
            <form @submit.prevent="addGames">
                <button type="submit" class="createGameButton">创建游戏</button>
            </form>
        </div>
    </div>
    </div>
</template>

<script>
import HeaderTopAfterLogin from "../smallcomponents/HeaderTopAfterLogin.vue";
import axios from "axios";

export default {
    data() {
        return {
            message: "", // 消息内容
            messageType: "", // 消息类型 (success, error, warning)
            role: "", // 用户组
            userId: "", // 用户 ID
            inputGameName: "", // 用户输入的游戏名
            inputMaxPlayers: 0, // 用户输入的最大玩家数
            createdGames: [], // 存储创建的游戏列表
            constants: [], // 存储常量
            variables: [], // 存储变量
            targetVariable: "", // 目标变量
            targetOrder: "asc", // 顺序或逆序
            showAddConstantModal: false, // 控制添加常量模态框的显示
            showVariableTypeSelector: false, // 控制变量类型选择器的显示
            selectedVariableType: "", // 用户选择的变量类型
            envVariable: {
                name: "",
                initialValue: 0,
                operator: "",
                operand: 0,
                everyRound: 1,
                display: false,
            },
            decisionVariable: {
                name: "",
                type: "enum", // 默认类型
                enumValues: "",
                conditionOperator: "",
                conditionValue: 0,
                numberType: "integer",
            },
            dependentVariable: {
                initialValue: 0,
                formula: "",
            },
            newConstant: {
                name: "",
                initialValue: 0,
                display: false,
            },
            environmentVariables: [], // 环境变量
            decisionVariables: [], // 决策变量
            dependentVariables: [], // 应变量
            environmentIndex: 1, // 环境变量索引
            decisionIndex: 1, // 决策变量索引
            dependentIndex: 1, // 应变量索引
        };
    },
    methods: {
        async checkTokenValidity() {
            const token = localStorage.getItem("token");
            if (!token) {
                this.$router.push({ path: "/Login" });
                return;
            }
            try {
                await axios.get("http://localhost:19198/protected", {
                    headers: { Authorization: token },
                });
            } catch (error) {
                if (!error.response) {
                    console.error("网络错误:", error);
                    alert("网络连接失败，请检查您的网络");
                } else {
                    console.error("Token 验证失败:", error);
                    alert("您的账号已在其他设备登录，请重新登录");
                }
                localStorage.removeItem("token");
                localStorage.removeItem("userId");
                localStorage.removeItem("role");
                this.$router.push({ path: "/Login" });
            }
        },
        async getCreatedGames() {
            try {
                const token = localStorage.getItem("token"); // 获取用户 token
                const response = await axios.get("http://localhost:19198/api/getCreatedGames", {
                    headers: {
                        Authorization: `Bearer ${token}`, // 发送 Bearer Token
                    },
                });
                if (response.data) {
                    console.log('获取到的游戏信息:', response.data);
                    this.createdGames = response.data; // 直接使用后端返回的数据
                } else {
                    console.warn("没有获取到任何创建的游戏");
                    this.createdGames = [];
                }
            } catch (error) {
                console.error('获取游戏信息失败:', error);
                this.createdGames = [];
            }
        },
        async addGames() {
            if (!window.confirm("确定要创建该游戏吗？")) {
                return;
            }
            const token = localStorage.getItem("token"); // 获取用户 token
            try {
                const response = await axios.post("http://localhost:19198/api/addGame", {
                    gameName: this.inputGameName, // 游戏名称
                    maxPlayers: this.inputMaxPlayers, // 最大玩家数
                    constants: this.constants, // 常量
                    variables: [
                        ...this.environmentVariables, // 环境变量
                        ...this.decisionVariables, // 决策变量
                        ...this.dependentVariables, // 应变量
                    ],
                    targetVariable: this.targetVariable, // 目标变量
                    targetOrder: this.targetOrder, // 目标变量排序方式
                }, {
                    headers: {
                        Authorization: `Bearer ${token}`, // 发送 Bearer Token
                    },
                });

                if (response.data.success) {
                    const returnMessage = response.data.message || "游戏添加成功";
                    this.setMessage(returnMessage, "success");
                    this.resetGameForm();
                } else {
                    const returnMessage = response.data.message || "游戏添加失败";//返回错误信息，如d2格式错误等
                    this.setMessage(returnMessage, "error");
                }
            } catch (error) {
                this.setMessage("添加游戏失败，请稍后再试", "error");
                console.error("添加游戏失败:", error);
            }
        },
        resetGameForm() {
            this.inputGameName = "";
            this.inputMaxPlayers = 0;
            this.constants = [];
            this.environmentVariables = [];
            this.decisionVariables = [];
            this.dependentVariables = [];
            this.targetVariable = "";
            this.targetOrder = "asc";
        },
        async deleteGame(gameId) {
            if (!window.confirm("确定要删除该游戏吗？")) {
                return;
            }
            const token = localStorage.getItem("token"); // 获取用户 token
            axios.post("http://localhost:19198/api/deleteGame", {
                gameId: gameId, // 游戏 ID
            }, {
                headers: {
                    Authorization: `Bearer ${token}`, // 发送 Bearer Token
                },
            })
                .then(response => {
                    if (response.data.success) {
                        this.setMessage("游戏删除成功", "success");
                        this.getCreatedGames(); // 刷新游戏列表
                    } else {
                        this.setMessage("游戏删除失败", "error");
                        console.error("删除游戏失败:", response.data.message);
                    }
                })
                .catch(error => {
                    console.error("删除游戏失败:", error);
                    this.setMessage("删除游戏失败，请稍后再试", "error");
                });
        },
        addConstant() {
            if (this.newConstant.name && this.newConstant.initialValue !== null) {
                this.constants.push({ ...this.newConstant });
                this.setMessage("常量添加成功！", "success");
                this.resetNewConstant();
            } else {
                this.setMessage("请填写完整的常量信息！", "warning");
            }
        },
        cancelAddConstant() {
            this.resetNewConstant();
        },
        resetNewConstant() {
            this.newConstant = {
                name: "",
                initialValue: 0,
                display: false,
            };
            this.showAddConstantModal = false;
        },
        addVariable() {
            if (this.selectedVariableType) {
                const name = prompt("请输入变量名称:");
                if (name) {
                    this.variables.push({ type: this.selectedVariableType, name });
                    this.showVariableTypeSelector = false; // 隐藏选择器
                    this.selectedVariableType = ""; // 重置选择
                }
            } else {
                this.setMessage("请选择变量类型！", "warning");
            }
        },
        cancelAddVariable() {
            this.showVariableTypeSelector = false; // 隐藏选择器
            this.selectedVariableType = ""; // 重置选择
        },
        setTargetVariable() {
            this.setMessage(`目标变量已设置为: ${this.targetVariable}，排序方式: ${this.targetOrder === "asc" ? "顺序" : "逆序"}`, "success");
        },
        confirmVariableType() {
            if (!this.selectedVariableType) {
                this.setMessage("请选择变量类型！", "warning");
                return;
            }
            // 如果变量类型已选择，直接返回，不再提示
            this.showVariableTypeSelector = false;
        },
        cancelAddVariable() {
            this.showVariableTypeSelector = false;
            this.selectedVariableType = "";
        },
        addEnvironmentVariable() {
            const validOperators = ["+", "-", "*", "/", "%"]; // 合法的操作符
            if (!validOperators.includes(this.envVariable.operator)) {
                this.setMessage("操作符不合法！合法的操作符有: +, -, *, /, %", "warning");
                return;
            }

            this.environmentVariables.push({
                id: `e${this.environmentIndex}`, // 生成环境变量索引
                type: "环境变量",
                ...this.envVariable,
            });
            this.environmentIndex++; // 增加索引
            this.resetEnvironmentVariable();
        },
        addDecisionVariable() {
            this.decisionVariables.push({
                id: `d${this.decisionIndex}`, // 生成决策变量索引
                type: "决策变量",
                typeDetail: this.decisionVariable.type,
                ...this.decisionVariable,
            });
            this.decisionIndex++; // 增加索引
            this.resetDecisionVariable();
        },
        addDependentVariable() {
            this.dependentVariables.push({
                id: `r${this.dependentIndex}`, // 生成应变量索引
                type: "应变量",
                ...this.dependentVariable,
            });
            this.dependentIndex++; // 增加索引
            this.resetDependentVariable();
        },
        resetEnvironmentVariable() {
            this.envVariable = {
                name: "",
                initialValue: 0,
                operator: "",
                operand: 0,
                everyRound: 1,
                display: false,
            };
            this.showVariableTypeSelector = false;
            this.selectedVariableType = "";
        },
        resetDecisionVariable() {
            this.decisionVariable = {
                name: "",
                type: "enum",
                enumValues: "",
                conditionOperator: "",
                conditionValue: 0,
                numberType: "integer",
            };
            this.showVariableTypeSelector = false;
            this.selectedVariableType = "";
        },
        resetDependentVariable() {
            this.dependentVariable = {
                initialValue: 0,
                formula: "",
            };
            this.showVariableTypeSelector = false;
            this.selectedVariableType = "";
        },
        setMessage(content, type) {
            this.message = content;
            this.messageType = type; // 设置消息类型
        },
        manageGame(gameId) {
            // 跳转到管理游戏界面，并传递游戏 ID
            this.checkTokenValidity(); // 检查 token 有效性
            this.$router.push({ path: `/ManageGame/${gameId}` });
        },
        deleteEnvironmentVariable(index) {
            if (window.confirm("确定要删除该环境变量吗？")) {
                this.environmentVariables.splice(index, 1);
                this.setMessage("环境变量已删除", "success");
            }
        },

        // 删除决策变量
        deleteDecisionVariable(index) {
            if (window.confirm("确定要删除该决策变量吗？")) {
                this.decisionVariables.splice(index, 1);
                this.setMessage("决策变量已删除", "success");
            }
        },

        // 删除应变量
        deleteDependentVariable(index) {
            if (window.confirm("确定要删除该应变量吗？")) {
                this.dependentVariables.splice(index, 1);
                this.setMessage("应变量已删除", "success");
            }
        },
        goBackToUserInfoPage() {
            this.checkTokenValidity(); // 检查 token 有效性
            this.$router.push({ path: "/UserInfo" });
        },
    },
    mounted() {
        console.log("CreatGamePage 已挂载");
        this.userId = localStorage.getItem("userId") || "未登录用户"; // 获取用户 ID
        this.role = localStorage.getItem("role") || ""; // 获取用户组
        this.checkTokenValidity(); // 检查 token 有效性
        this.getCreatedGames(); // 获取创建的游戏列表
    },
    components: {
        HeaderTopAfterLogin,
    },
    computed: {
        allVariables() {
            return [
                ...this.environmentVariables,
                ...this.decisionVariables,
                ...this.dependentVariables,
            ];
        },
    }
};
</script>

<style scoped>
/* 样式可以根据需要调整 */
.message-box {
    position: fixed;
    /* 固定在页面上 */
    top: 0;
    /* 距离页面顶部 0 */
    left: 50%;
    /* 水平居中 */
    transform: translateX(-50%);
    /* 将元素的水平中心对齐到页面中心 */
    z-index: 1000;
    /* 确保消息框在其他内容之上 */
    padding: 10px;
    margin: 0;
    /* 移除默认的外边距 */
    border-radius: 5px;
    font-size: 14px;
    text-align: center;
    width: 80%;
    /* 可根据需要调整宽度 */
    max-width: 600px;
    /* 限制最大宽度 */
}

.message-box.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.message-box.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.message-box.warning {
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffeeba;
}

.createGameButton {
    display: block;
    margin: 20px auto;
    padding: 10px 20px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    text-align: center;
}

.createGameButton:hover {
    background-color: #218838;
}
.goBackToUserInfoPageButton {
    float: right; 
    margin-top: -10px
}

form {
    margin-top: 20px;
}

form div {
    margin-bottom: 10px;
}

label {
    display: block;
    margin-bottom: 5px;
}

input {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
}

button {
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;
}

button:hover {
    background-color: #0056b3;
}

h2 {
    margin-top: 20px;
}

ul {
    list-style: none;
    padding: 0;
}

li {
    margin-bottom: 10px;
}

button {
    margin-top: 10px;
    padding: 5px 10px;
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;
}

button:hover {
    background-color: #0056b3;
}

label {
    margin-right: 10px;
}
</style>
