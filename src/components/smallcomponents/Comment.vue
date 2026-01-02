<template>
    <a-comment
      author="Socrates"
      content="Comment body content."
      datetime="1 hour"
    >
      <template #actions>
        <span class="action" @click="onLikeChange">
          <span v-if="like">
            <IconHeartFill :style="{ color: '#f53f3f' }" />
          </span>
          <span v-else>
            <IconHeart />
          </span>
          {{ 83 + (like ? 1 : 0) }}
        </span>
        <span class="action" @click="onStarChange">
          <span v-if="star">
            <IconStarFill :style="{ color: '#ffb400' }" />
          </span>
          <span v-else>
            <IconStar />
          </span>
          {{ 3 + (star ? 1 : 0) }}
        </span>
        <span class="action">
          <IconMessage /> Reply
        </span>
      </template>
      <template #avatar>
        <a-avatar>
          <img
            alt="avatar"
            src="https://p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/3ee5f13fb09879ecb5185e440cef6eb9.png~tplv-uwbnlip3yd-webp.webp"
          />
        </a-avatar>
      </template>
    </a-comment>
  </template>
  
  <script>
  import { ref } from 'vue';
  import {
    IconHeart,
    IconMessage,
    IconStar,
    IconStarFill,
    IconHeartFill,
  } from '@arco-design/web-vue/es/icon';
  
  export default {
    components: {
      IconHeart,
      IconMessage,
      IconStar,
      IconStarFill,
      IconHeartFill,
    },
    setup() {
      const like = ref(false);
      const star = ref(false);
      const onLikeChange = () => {
        like.value = !like.value;
      };
      const onStarChange = () => {
        star.value = !star.value;
      };
  
      return {
        like,
        star,
        onLikeChange,
        onStarChange,
      };
    },
  };
  </script>
  
  <style scoped>
  .action {
    display: inline-block;
    padding: 0 4px;
    color: var(--color-text-1);
    line-height: 24px;
    background: transparent;
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.1s ease;
  }
  .action:hover {
    background: var(--color-fill-3);
  }
  </style>
