<template>
  <div>
    <p>
      {{ label }}:{{ result ? result : "暂无数据" }}
    </p>
  </div>
</template>

<script>
export default {
  name: "ResultOutput",
  props: {
    result: {
      type: [String, Number, null], // 支持字符串、数字和 null
      default: null, // 默认值为 null
    },
    label: {
      type: String,
      default: "结果", // 结果的标签
    },
  },
};
</script>

<style scoped>
/* 样式可以根据需要调整 */
</style>