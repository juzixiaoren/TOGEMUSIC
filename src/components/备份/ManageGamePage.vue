<template>
    <div>
        <!-- 顶部导航栏 -->
        <HeaderTopAfterLogin :userId="userId" :role="role"></HeaderTopAfterLogin>
        <!-- Your content goes here -->
          <!-- 游戏管理界面 -->
          <div v-if="message" class="message-box" :class="messageType">
            {{ message }}
        </div>
        <div>
            <h1>管理游戏</h1>
            <p>当前管理的游戏 ID: {{ gameId }}</p>
            <p>游戏状态: {{ gameStatus }}</p>

            <!-- 玩家列表 -->
            <h2>玩家列表</h2>
            <ul>
                <li v-for="player in players" :key="player.userId">
                    用户名: {{ player.userName }} - 用户组: {{ player.role }}
                </li>
            </ul>

            <!-- 加入申请列表 -->
            <h2>加入申请</h2>
            <ul v-if="joinRequests.length > 0">
                <li v-for="request in joinRequests" :key="request.userId">
                    用户名: {{ request.userName }} - 用户组: {{ request.role }}
                    <button @click="approveJoinRequest(request.userId)">批准</button>
                    <button @click="rejectJoinRequest(request.userId)">拒绝</button>
                </li>
            </ul>
            <p v-else>暂无加入申请。</p>
        </div>

    </div>
</template>

<script>
import HeaderTopAfterLogin from '../smallcomponents/HeaderTopAfterLogin.vue';
import axios from 'axios';
export default {
    data() {
        return {
            // Your data properties go here
            userId: '', // 用户 ID
            role: '', // 用户组
            gameId: '', // 游戏 ID
            gameStatus: '', // 游戏状态
            players: [], // 玩家列表
            joinRequests: [], // 加入申请列表
        };
    },
    methods: {
        // Your methods go here
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
        async getPlayerList() {
            try {
                const token = localStorage.getItem("token");
                const response = await axios.get('http://localhost:19198/api/getPlayerList', {
                    params: { gameId: this.gameId, token },
                });
                if (response.data) {
                    this.players = response.data;
                } else {
                    this.players = [];
                }
            } catch (error) {
                console.error('获取玩家列表失败:', error);
            }
        },
         // 获取玩家列表
         async getPlayerList() {
            try {
                const token = localStorage.getItem("token");
                const response = await axios.get('http://localhost:19198/api/getPlayerList', {
                    params: { gameId: this.gameId },
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (response.data) {
                    this.players = response.data.players;
                    this.gameStatus = response.data.gameStatus;
                } else {
                    this.players = [];
                    this.gameStatus = "未知";
                }
            } catch (error) {
                console.error('获取玩家列表失败:', error);
            }
        },

        // 获取加入申请列表
        async getJoinRequests() {
            try {
                const token = localStorage.getItem("token");
                const response = await axios.get('http://localhost:19198/api/getJoinRequests', {
                    params: { gameId: this.gameId },
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (response.data) {
                    this.joinRequests = response.data;
                } else {
                    this.joinRequests = [];
                }
            } catch (error) {
                console.error('获取加入申请失败:', error);
            }
        },

        // 批准加入申请
        async approveJoinRequest(userId) {
            try {
                const token = localStorage.getItem("token");
                const response = await axios.post('http://localhost:19198/api/approveJoinRequest', {
                    gameId: this.gameId,
                    userId: userId,
                }, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (response.data.success) {
                    this.setMessage("加入申请已批准", "success");
                    this.getJoinRequests(); // 刷新加入申请列表
                    this.getPlayerList(); // 刷新玩家列表
                } else {
                    this.setMessage("批准失败", "error");
                }
            } catch (error) {
                console.error('批准加入申请失败:', error);
                this.setMessage("批准失败，请稍后再试", "error");
            }
        },

        // 拒绝加入申请
        async rejectJoinRequest(userId) {
            try {
                const token = localStorage.getItem("token");
                const response = await axios.post('http://localhost:19198/api/rejectJoinRequest', {
                    gameId: this.gameId,
                    userId: userId,
                }, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (response.data.success) {
                    this.setMessage("加入申请已拒绝", "success");
                    this.getJoinRequests(); // 刷新加入申请列表
                } else {
                    this.setMessage("拒绝失败", "error");
                }
            } catch (error) {
                console.error('拒绝加入申请失败:', error);
                this.setMessage("拒绝失败，请稍后再试", "error");
            }
        },
        async getGameStatus() {
            try {
                const token = localStorage.getItem("token");
                const response = await axios.get('http://localhost:19198/api/getGameStatus', {
                    params: { gameId: this.gameId },
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (response.data) {
                    this.gameStatus = response.data.status;
                } else {
                    this.gameStatus = "未知";
                }
            } catch (error) {
                console.error('获取游戏状态失败:', error);
            }
        },

        // 设置消息提示
        setMessage(content, type) {
            this.message = content;
            this.messageType = type; // success, error, warning
            setTimeout(() => {
                this.message = null; // 清除消息提示
            }, 3000); // 3秒后清除消息提示
        },
    },
    computed: {
        // Your computed properties go here
    },
    mounted() {
        // Lifecycle hook
        this.userId = localStorage.getItem("userId") || "未登录用户";
        this.role = localStorage.getItem("role") || ""; // 获取用户组
        this.gameId = this.$route.params.gameId; // 获取路由参数中的游戏 ID
        this.checkTokenValidity(); // 检查 token 有效性
        this.getPlayerList(); // 获取玩家列表
        this.getJoinRequests(); // 获取加入申请列表
        this.getGameStatus(); // 获取游戏状态
    },
    components: {
        HeaderTopAfterLogin,
    },
};
</script>

<style scoped>
/* Your styles go here */
.message-box {
    padding: 10px;
    margin: 10px 0;
    border-radius: 5px;
    font-size: 14px;
    text-align: center;
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
</style>
