<template>
  <t-popup expand-animation placement="bottom-right" trigger="click">
    <template #content>
      <div class="header-msg">
        <div class="header-msg-top">
          <p>{{ t('layout.notice.title') }}</p>
          <t-button
            v-if="unreadMsg.length > 0"
            class="clear-btn"
            variant="text"
            theme="primary"
            @click="setRead('all')"
            >{{ t('layout.notice.clear') }}</t-button
          >
        </div>
        <t-list v-if="unreadMsg.length > 0" class="narrow-scrollbar" :split="false">
          <t-list-item v-for="(item, index) in visibleMessages" :key="index">
            <div>
              <p class="msg-content">{{ item.content }}</p>
              <p class="msg-type">{{ item.type }}</p>
            </div>
            <p class="msg-time">{{ item.date }}</p>
          </t-list-item>
        </t-list>

        <div v-else class="empty-list">
          <img src="https://tdesign.gtimg.com/pro-template/personal/nothing.png" alt="空" />
          <p>{{ t('layout.notice.empty') }}</p>
        </div>
        <div v-if="unreadMsg.length > 0" class="header-msg-bottom">
          <t-button class="header-msg-bottom-link" variant="text" theme="default" block @click="goDetail">
            {{ t('layout.notice.viewAll') }}
          </t-button>
        </div>
      </div>
    </template>
    <t-badge :count="unreadMsg.length" :offset="[4, 4]">
      <t-button theme="default" shape="square" variant="text">
        <t-icon name="mail" />
      </t-button>
    </t-badge>
  </t-popup>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { ref, computed } from 'vue';

import { t } from '@/locales';
import { useNotificationStore } from '@/store';
import type { NotificationItem } from '@/types/interface';

const router = useRouter();
const store = useNotificationStore();
const { msgData } = storeToRefs(store);

// 是否显示全部消息
const showAll = ref(false);

// 计算未读消息
const unreadMsg = computed(() => msgData.value.filter((item) => item.status));

// 计算当前显示的消息
const visibleMessages = computed(() => {
  return showAll.value ? unreadMsg.value : unreadMsg.value.slice(0, 2);
});

// 设置消息为已读
const setRead = (type: string, item?: NotificationItem) => {
  if (type === 'all') {
    msgData.value.forEach((e) => {
      e.status = false;
    });
  } else {
    const target = msgData.value.find((e) => e.id === item?.id);
    if (target) {
      target.status = false;
    }
  }
};

// 跳转到详情页或切换显示全部消息
const goDetail = () => {
  if (unreadMsg.value.length > 2) {
    showAll.value = !showAll.value; // 切换显示全部消息
  } else {
    router.push('/detail/secondary'); // 跳转到详情页
  }
};
</script>

<style lang="less" scoped>
.header-msg {
  width: 400px;
  margin: calc(0px - var(--td-comp-paddingTB-xs)) calc(0px - var(--td-comp-paddingLR-s));

  .empty-list {
    text-align: center;
    padding: var(--td-comp-paddingTB-xxl) 0;
    font: var(--td-font-body-medium);
    color: var(--td-text-color-secondary);

    img {
      width: var(--td-comp-size-xxxxl);
    }

    p {
      margin-top: var(--td-comp-margin-xs);
    }
  }

  &-top {
    position: relative;
    font: var(--td-font-title-medium);
    color: var(--td-text-color-primary);
    text-align: left;
    padding: var(--td-comp-paddingTB-l) var(--td-comp-paddingLR-xl) 0;
    display: flex;
    align-items: center;
    justify-content: space-between;

    .clear-btn {
      right: calc(var(--td-comp-paddingTB-l) - var(--td-comp-paddingLR-xl));
    }
  }

  &-bottom {
    align-items: center;
    display: flex;
    justify-content: center;
    padding: var(--td-comp-paddingTB-s) var(--td-comp-paddingLR-s);
    border-top: 1px solid var(--td-component-stroke);

    &-link {
      text-decoration: none;
      cursor: pointer;
      color: var(--td-text-color-placeholder);
    }
  }

  .t-list {
    max-height: 300px; /* 设置最大高度 */
    overflow-y: auto; /* 添加垂直滚动条 */
    padding: var(--td-comp-margin-s) var(--td-comp-margin-s);
  }

  .t-list-item {
    overflow: hidden;
    width: 100%;
    padding: var(--td-comp-paddingTB-l) var(--td-comp-paddingLR-l);
    border-radius: var(--td-radius-default);
    font: var(--td-font-body-medium);
    color: var(--td-text-color-primary);
    cursor: pointer;
    transition: background-color 0.2s linear;

    &:hover {
      background-color: var(--td-bg-color-container-hover);

      .msg-content {
        color: var(--td-brand-color);
      }

      .t-list-item__action {
        button {
          bottom: var(--td-comp-margin-l);
          opacity: 1;
        }
      }

      .msg-time {
        bottom: -6px;
        opacity: 0;
      }
    }

    .msg-content {
      margin-bottom: var(--td-comp-margin-s);
    }

    .msg-type {
      color: var(--td-text-color-secondary);
    }

    .t-list-item__action {
      button {
        opacity: 0;
        position: absolute;
        right: var(--td-comp-margin-xxl);
        bottom: -6px;
      }
    }

    .msg-time {
      transition: all 0.2s ease;
      opacity: 1;
      position: absolute;
      right: var(--td-comp-margin-xxl);
      bottom: var(--td-comp-margin-l);
      color: var(--td-text-color-secondary);
    }
  }
}
</style>
