<template>
   <div class="top">
        <div class="title">
            <h1>TOGEMUSIC</h1>
            <div class="welcome">
                <h2>欢迎，{{ userId }}</h2>
                <button @click="logout">退出登录</button>
            </div>
        </div>
         <div class="amiya" onclick="replaceimgamiya()">
            <img src="/src/assets/images/amiya.gif" alt="阿米娅" height="200px" id="amiyaimg">
         </div>
    </div>
</template>

<script>

export default {
    name: "HeaderTopAfterLogin",
    props: {
        userId: {
            type: String,
            default: "未登录用户",
        },
    },
    methods: {
        logout() {
        localStorage.removeItem("token"); // 清除 token
        localStorage.removeItem("userId"); // 清除用户 ID
        this.$router.push({ path: "/Login" }); // 跳转到登录页面
        },
    },
};
</script>

<style scoped>
.top{
    width: 100vw;
    height: 120px;
    overflow: hidden;
    position: fixed; 
    background-color: rgba(255, 255, 255, 0.5);
    flex-direction: row-reverse;
    
    backdrop-filter: blur(1px);
    /* background-image: url("/src/assets/images/backgroundimg.jpg"); */
    background-size: cover;
    box-shadow: 0px 5px 15px rgba(94, 93, 93, 0.5);
    
    z-index: 999;
    box-sizing: border-box; /* 确保 padding 和 border 不会增加额外尺寸 */
    border-bottom: 1px solid rgba(255, 255, 255, 0.115); /* 添加底部边框 */
}
.title{
    width: 100%;


    position:absolute;
    bottom: 0;

    font-family: 'MCFont';
    color: rgb(44, 44, 44);
    margin-left: 50px;
    margin-bottom: -10px;
}
.logo{
    position:absolute;
    bottom: 0;
    right: 0;
    margin-right: 150px;
}
.amiya{
    position: relative;
    left: 400px;
    top: -78px;
    opacity: 0;
    transition: opacity 1300ms;
}
.amiya:hover{
    opacity: 1;
}
.welcome {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 16px;
    margin-top: 8px;
}
</style>