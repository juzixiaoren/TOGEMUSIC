<template>
   <div class="top">
        <div class="title">
            <h1>TOGEMUSIC</h1>
        </div>
        <div class="logo">
            <!-- <img id="logo" src="/src/assets/images/logo.png" alt="logo" height="200px"> -->
         </div>
         <div class="amiya" onclick="replaceimgamiya()">
            <img src="/src/assets/images/amiya.gif" alt="阿米娅" height="200px" id="amiyaimg">
         </div>
    </div>
</template>

<script>
export default {
    name: "ComponentTemplate",
    data() {
        return {
            title: "Component Template",
        };
    },
    methods: {
        // Add your methods here
    },
    watch: {
        // Add your watchers here
    },
    computed: {
        // Add your computed properties here
    },
    mounted() {
        console.log("Component mounted");
    },
};
</script>

<style scoped>
.top{
    width: 100vw;
    height: 120px;
    overflow: hidden;
    position: fixed; 
    background-color: rgba(65, 65, 65, 0.15);
    flex-direction: row-reverse;
    
    backdrop-filter: blur(5px) brightness(200%) contrast(110%);
    /* background-image: url("/src/assets/images/backgroundimg.jpg"); */
    background-size: cover;
    box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.5);
    
    z-index: 999;
    box-sizing: border-box; /* 确保 padding 和 border 不会增加额外尺寸 */
    border-bottom: 1px solid rgba(255, 255, 255, 0.115); /* 添加底部边框 */
}
.title{
    width: 100%;


    position:absolute;
    bottom: 0;

    font-family: 'MyFont';
    color: white;
    margin-left: 50px;
    margin-bottom: 10px;
}
.amiya{
    position: relative;
    left: 1137px;
    top: -197px;
    opacity: 0;
    transition: opacity 1300ms;
}
.amiya:hover{
    opacity: 1;
}
</style>
