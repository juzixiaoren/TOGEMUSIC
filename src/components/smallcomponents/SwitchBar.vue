<template>

  <div class="switch-bar" ref="switchBar" :class="{ 'bar-shake': isBarShaking }">
    <!-- 循环渲染每个按钮和分隔线 -->

    <div 
      v-for="(option, index) in options" 
      :key="option.value" 
      class="button-wrapper"
    >
      <!-- 按钮 -->
      <button
        class="switch-button"
        :class="{ active: modelValue === option.value, 'animate-hit': activeButton === option.value }"
        @click="handleClick(option.value)"
        ref="animationButton"
      >
        {{ option.label }}
      </button>

    </div>
  </div>
</template>

<script>
import axios from 'axios';
import strikeSound from '/src/assets/audio/metal_light_1.wav';

export default {
  name: 'SwitchBar', 

  props: {
    modelValue: {
      type: [String, Number],
      required: true
    },
    options: {
      type: Array,
      required: true,
      default: () => [] // 确保 options 是从外部传入的
    }
  },
  components: {
    axios,
    strikeSound
  },
  data() {
    return {
      activeButton: null,
      isBarShaking: false,
    };
  },
  computed: {
  },
  mounted() {
    window.addEventListener('keydown', this.handleKeydown);
  },
  beforeDestroy() {
    window.removeEventListener('keydown', this.handleKeydown);
  },
  methods: {
    async handleClick(valueOfSelectedOption) {
      // 验证 Token
      const isValid = await this.checkTokenValidity();
      if (!isValid) return;

      // 更新选中值
      this.$emit('update:modelValue', valueOfSelectedOption);
      this.triggerAnimation(valueOfSelectedOption);
      this.triggerBarShake();

      const audio = new Audio(strikeSound);
      audio.play().catch(err => console.log('音频播放失败:', err));
    },
    async checkTokenValidity() {
      const token = localStorage.getItem("token");
      if (!token) {
        this.$router.push({ path: "/Login" });
        return false;
      }
      try {
        await axios.get("http://localhost:19198/protected", {
          headers: { Authorization: token },
        });
        return true;
      } catch (error) {
        if (!error.response) {
          console.error("网络错误:", error);
          alert("网络连接失败，请检查您的网络");
        } else {
          console.error("Token 验证失败:", error);
          alert("您的账号已在其他设备登录，请重新登录");
        }
        localStorage.removeItem("token");
        this.$router.push({ path: "/Login" });
        return false;
      }
    },
    handleKeydown(event) {
      if (event.key === 'ArrowUp') {
        this.navigateOptions(-1); // 上方向键
      } else if (event.key === 'ArrowDown') {
        this.navigateOptions(1); // 下方向键
      }
    },
    navigateOptions(direction) {
      const currentIndex = this.options.findIndex(option => option.value === this.modelValue);
      let newIndex = currentIndex + direction;

      // 循环切换
      if (newIndex < 0) {
        newIndex = this.options.length - 1;
      } else if (newIndex >= this.options.length) {
        newIndex = 0;
      }

      this.handleClick(this.options[newIndex].value);
    },
    triggerAnimation(value) {
      this.activeButton = value;
      setTimeout(() => {
        this.activeButton = null;
      }, 1000);
    },
    triggerBarShake() {
    },
  }
};
</script>

<style scoped>
.switch-bar {
  display: flex;
  flex: 0 0 0;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 40px;


  width: 100%;
  height: 100%;
  transition: transform 0.1s ease-in-out;

  background-image: radial-gradient(rgba(255, 255, 255, 0.149), rgba(152, 152, 152, 0.076));
  border-width: 2px 1px;
  border-style: solid;
  border-color: rgba(255, 255, 255, 0.3);
  border-radius: 30px; 
  box-shadow: 0 4px 80px rgba(0, 0, 0, 0.5);
  backdrop-filter:  blur(8px) brightness(150%) contrast(120%);
}
.button-wrapper {
  display: flex;
  flex-grow: 0;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
  align-items: space-evenly;
  width: 100%;
}

.switch-button {
  background-color: rgba(224, 46, 46, 0);
  background-image: radial-gradient(rgba(255, 255, 255, 0.149), rgba(152, 152, 152, 0.076));
  border-width: 2px 1px;
  border-style: solid;
  border-color: rgba(255, 255, 255, 0.3);
  border-radius: 15px; 
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);

  backdrop-filter:  blur(8px) brightness(150%) contrast(120%);
  flex: 0;
  color: rgb(255, 255, 255);
  font-size: 16px;
  font-family: 'MyFont';
  padding: 10px 20px;
  margin: 0 5px;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s ease, box-shadow 0.6s, transform 0.3s ease-out;
  outline: none;
}

.switch-button:hover {
  transform: scale(1.05);
  background-color: rgba(232, 232, 232, 0.18);
  transition: 0.5s;
  transition-timing-function: cubic-bezier(0,.68,.12,1);
}

.switch-button.active {
  background-color: rgba(14, 99, 47, 0.619);
  border-color: rgba(113, 255, 172, 0.455);
  transition: 0.5s;
  font-weight: bold;
  box-shadow: 0 0 20px rgba(126, 255, 103, 0.5);
}
</style>

