<template>
  <t-form
    ref="form"
    :class="['item-container', `login-${type}`]"
    :data="formData"
    :rules="FORM_RULES"
    label-width="0"
    @submit="onSubmit"
  >
    <template v-if="type == 'password'">
      <t-form-item name="account">
        <t-input v-model="formData.account" size="large" :placeholder="`${t('pages.login.input.account')}：admin`">
          <template #prefix-icon>
            <t-icon name="user" />
          </template>
        </t-input>
      </t-form-item>

      <t-form-item name="password">
        <t-input
          v-model="formData.password"
          size="large"
          :type="showPsw ? 'text' : 'password'"
          clearable
          :placeholder="`${t('pages.login.input.password')}：admin`"
        >
          <template #prefix-icon>
            <t-icon name="lock-on" />
          </template>
          <template #suffix-icon>
            <t-icon :name="showPsw ? 'browse' : 'browse-off'" @click="showPsw = !showPsw" />
          </template>
        </t-input>
      </t-form-item>

      <div class="check-container remember-pwd">
        <t-checkbox>{{ t('pages.login.remember') }}</t-checkbox>
        <span class="tip">{{ t('pages.login.forget') }}</span>
      </div>
    </template>

    <t-form-item v-if="type !== 'qrcode'" class="btn-container">
      <t-button block size="large" type="submit" :loading="isLoading">
        {{ t('pages.login.signIn') }}
      </t-button>
    </t-form-item>

    <div class="switch-container">
      <span v-if="type !== 'password'" class="tip" @click="switchType('password')">{{
        t('pages.login.accountLogin')
      }}</span>
    </div>
  </t-form>
</template>

<script setup lang="ts">
import {FormInstanceFunctions, FormRule, MessagePlugin, SubmitContext} from 'tdesign-vue-next';
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { t } from '@/locales';
import { useUserStore } from '@/store';
import { getSysUserByAccount } from '@/api/services/sysUser';

const userStore = useUserStore();

const INITIAL_DATA = {
  phone: '',
  account: 'admin',
  password: 'admin',
  verifyCode: '',
  checked: false,
};

const FORM_RULES: Record<string, FormRule[]> = {
  phone: [{ required: true, message: t('pages.login.required.phone'), type: 'error' }],
  account: [{ required: true, message: t('pages.login.required.account'), type: 'error' }],
  password: [{ required: true, message: t('pages.login.required.password'), type: 'error' }],
  verifyCode: [{ required: true, message: t('pages.login.required.verification'), type: 'error' }],
};

const type = ref('password');
const form = ref<FormInstanceFunctions>();
const formData = ref({ ...INITIAL_DATA });
const showPsw = ref(false);
const isLoading = ref(false);

const switchType = (val: string) => {
  type.value = val;
};

const router = useRouter();
const route = useRoute();

const onSubmit = async (ctx: SubmitContext) => {
  isLoading.value = true;
  if (ctx.validateResult === true) {
    try {
      const data = await getSysUserByAccount(formData.value.account, formData.value.password);
      if (data.code === 200) {
        userStore.token = data.data.access_token;
        userStore.userInfo.name = data.data.user.account;
        const redirect = route.query.redirect as string;
        const redirectUrl = redirect ? decodeURIComponent(redirect) : '/dashboard';
        await router.push(redirectUrl);
        MessagePlugin.info({ content: '登录成功', duration: 2000 });
      }
    } catch (e) {
      // pass
    } finally {
      isLoading.value = false; // 移至finally以确保总是能结束加载状态
    }
  } else {
    // 如果验证失败，确保加载状态也被重置
    isLoading.value = false;
  }
};
</script>

<style lang="less" scoped>
@import '../index.less';
</style>
