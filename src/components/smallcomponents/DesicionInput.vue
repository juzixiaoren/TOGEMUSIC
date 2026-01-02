<template >
  <div style="font-family: 'MyFont';">
    <div style="overflow: hidden;">
      <label class="label">{{ label }}</label>
      <input
        v-model="inputValue"
        :placeholder="placeholder"
        @input="updateValue"
        class="input"
      />
    </div>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script>
export default {
  name: "DesicionInput",
  props: {
    label: {
      type: String,
      default: "请输入信息",
    },
    placeholder: {
      type: String,
      default: "请输入内容",
    },
    fieldName: {
      type: String,
      default: "data",
    },
    modelValue: {
      type: [String, Number],
      default: "",
    },
  },
  data() {
    return {
      inputValue: this.modelValue, // 初始化输入值
      errorMessage: "",
    };
  },
  methods: {
    updateValue() {
      this.$emit("update:modelValue", this.inputValue); // 将输入值传递给父组件
    },
  },
};
</script>

<style scoped>
.error {
  color: red;
  font-size: 14px;
}

.label {
  color: white;
  font-size: 16px;
  font-weight: bold;
  padding: 15px 20px;
  margin: 10px;
  text-align: center;
  cursor: pointer;
  background-color: rgba(255, 255, 255, 0);
  border: 2px solid white;
  border-radius: 20px;
  box-shadow: 0 0 px 0px rgba(0, 0, 0, 0.5);
  transition: background-color 0.3s, color 0.3s ease, box-shadow 0.6s, transform 0.3s ease-out;
  min-width: 40px;
}

.input {
  flex: 0 0 0;

  box-sizing: border-box;
  width: 60%;
  height: 50px;
  border: 0;

  font-family: 'MyFont';
  font-size: 14px ;
  font-weight: normal;
  color: rgb(255, 255, 255);

  
  border-width: 2px 0;
  border-style: solid;
  background-color: rgba(118, 118, 118, 0.563);
  border-color:rgba(255, 255, 255, 0.455);
  border-radius: 30px; /* Example border radius */

  
  padding-left: 20px;
  margin-right: 20px;

  outline: none;

  transition: 0.3s;

}
.input:deep(.arco-input) {
  color: #ffffff;        /* 文字颜色 */
  font-size: 15px;    /* 字体大小 */
  font-weight: bold;
}
.input::placeholder {
  color: #ffffff;        /* 文字颜色 */

  font-size: 15px;    /* 字体大小 */
  opacity: 0.5;       /* 透明度 */
  font-style: italic; /* 斜体效果 */
}
/* 聚焦样式 */
.input:hover, .input:focus-within {
  border-color: #ffffffcb;
  background-color: rgba(176, 176, 176, 0.563);
  /* box-shadow: 0 0 20px rgba(255, 255, 255, 0.5); */
  
}


</style>