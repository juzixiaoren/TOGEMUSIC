<template>
  <!-- 多按钮栏容器 -->
  <!-- <div class="lottie-container" :style="{ transform: `translateY(${lottiePosition}px)` }">
    <DotLottieVue 
      class="spark"
      ref="sparkRef"
      autoplay
      loop
      src="/src/assets/lottie/spark.lottie" 
    />
  </div> -->
  <div class="switch-bar" ref="switchBar" :class="{ 'bar-shake': isBarShaking }">
    <!-- 循环渲染每个按钮和分隔线 -->
    <div class="line"></div>
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
      <div class="line"></div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import strikeSound from '/src/assets/audio/strike1.wav';
import { DotLottieVue } from '/node_modules/@lottiefiles/dotlottie-vue';

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
    DotLottieVue,
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
    lottiePositions() {
      return [-900 / (2 * this.options.length + 1), 10, 1000 / (2 * this.options.length + 1)]; // 根据按钮的数量和位置设置动画位置
    },
    lottiePosition() {
      const index = this.options.findIndex(option => option.value === this.modelValue);
      return this.lottiePositions[index] || 0;
    }
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
      const bar = this.$refs.switchBar;
      if (bar) {
        bar.classList.remove('bar-shake');
        void bar.offsetWidth;
        this.isBarShaking = true;
        setTimeout(() => {
          this.isBarShaking = false;
        }, 200);
      }
    },
  }
};
// 播放 Lottie 动画
      // const sparkRef = this.$refs.sparkRef;
      // if (sparkRef) {
      //   const dotLottie = sparkRef.getDotLottieInstance();
      //   if (dotLottie) {
      //     // 正确方法：先停止→重置→播放
      //     await dotLottie.stop();
      //     dotLottie.setFrame(0); // 强制回到第一帧
      //     dotLottie.play();      // 开始播放
      //   }
      // }
</script>

<style scoped>
.switch-bar {
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  align-items: center;
  width: 100%;
  height: 100%;
  transition: transform 0.1s ease-in-out;
}

.switch-bar.bar-shake {
  animation: bar-shake-animation 0.2s cubic-bezier(0.36, 0.07, 0.19, 0.97);
}

@keyframes bar-shake-animation {
  0% {
    transform: translateY(0);
  }
  20% {
    transform: translateY(-4px);
  }
  40% {
    transform: translateY(4px);
  }
  60% {
    transform: translateY(-2px);
  }
  80% {
    transform: translateY(2px);
  }
  100% {
    transform: translateY(0);
  }
}

.button-wrapper {
  display: flex;
  flex: auto;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.switch-button {
  flex: 0;
  color: white;
  font-weight: bold;
  padding: 10px;
  margin: 10px;
  text-align: center;
  cursor: pointer;
  background-color: rgba(255, 255, 255, 0);
  border: 2px solid white;
  border-radius: 0px;
  box-shadow: 0 0 10px 0px rgba(0, 0, 0, 0.5);
  transition: background-color 0.3s, color 0.3s ease, box-shadow 0.6s, transform 0.3s ease-out;
}

.switch-button:hover {
  box-shadow: 0 0 30px 2px rgba(216, 251, 255, 0.9);
  transition: box-shadow 0.2s;
}

.switch-button.active {
  background-color: #ffffff;
  color: rgb(0, 0, 0);
  transition: background-color 0.2s, color 0.7s ease, box-shadow 0.6s;
}

.switch-button.animate-hit {
  animation: hit-animation 0.1s cubic-bezier(0.68, -0.55, 0.27, 1.55);
}

@keyframes hit-animation {
  0% {
    transform: translate(0);
  }
  20% {
    transform: translate(-10px);
  }
  40% {
    transform: translate(20px);
  }
  60% {
    transform: translate(-6px);
  }
  80% {
    transform: translate(6px);
  }
  100% {
    transform: translate(0);
  }
}

.line {
  flex: auto;
  width: 3px;
  background-color: #ffffff;
  margin: 5% 5%;
  box-shadow: 0 0 10px 2px rgba(0, 0, 0, 0.3);
}

.spark {
  width: 200px;
  height: 200px;
  position: absolute;
  pointer-events: none;
  rotate: -9deg;
  scale: -1 1;
}
.lottie-container {
  position: absolute;
  pointer-events: none;
  translate: -200px 50px
}

</style>

