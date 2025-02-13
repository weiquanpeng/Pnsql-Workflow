<template>
  <t-space>
    <t-dialog
      v-model:visible="visible"
      header="用户信息"
      width="40%"
      :confirm-on-enter="false"
      :on-cancel="onCancel"
      :on-esc-keydown="onEscKeydown"
      :on-close-btn-click="onCloseBtnClick"
      :on-overlay-click="onOverlayClick"
      :on-confirm="handleSubmit"
      :confirm-loading="loading"
    >
      <t-space direction="vertical" style="width: 95%">
        <t-form ref="formRef" :data="form" :rules="rules" @validate="onValidate">
          <t-form-item label="用户" name="account">
            <t-input v-model="form.account" placeholder="Enter account" />
          </t-form-item>
          <t-form-item label="邮箱" name="email">
            <t-input v-model="form.email" placeholder="Enter email" />
          </t-form-item>
          <t-form-item label="密码" name="password">
            <t-input v-model="form.password" placeholder="Enter password" type="password" />
          </t-form-item>
          <t-form-item label="电话" name="phone">
            <t-input v-model="form.phone" placeholder="Enter phone number" />
          </t-form-item>
          <t-form-item label="是否激活" name="enable">
            <t-switch v-model="form.enable" :true-value="1" :false-value="0" />
          </t-form-item>
        </t-form>
      </t-space>
    </t-dialog>
  </t-space>
</template>

<script setup>
import { ref, watch, defineProps } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next'; // 引入消息插件
import { SysAddUser } from '@/api/services/sysUser';

// 接收父组件传递的方法
const props = defineProps({
  onRefresh: Function // 声明传递方法的类型
});

const visible = ref(false);
const loading = ref(false);

const formRef = ref(null);
const initialFormData = {
  account: '',
  email: '',
  password: '',
  phone: '',
  enable: true, // 使用布尔值作为初始状态
};
const form = ref({ ...initialFormData });

const rules = {
  account: [{ required: true, message: '必填', type: 'warning' }],
  password: [
    { required: true, message: '必填', type: 'warning' },
    {
      validator: (value) => value.length >= 6,
      message: '密码长度至少为6位',
      type: 'warning',
    },
  ],
  email: [{ type: 'warning', message: 'Email is optional' }],
  phone: [{ type: 'warning', message: 'Phone number is optional' }],
  enable: [{ type: 'warning', message: 'Enable status is optional' }],
};

const onValidate = ({ errorFields }) => {
  if (errorFields && errorFields.length > 0) {
    errorFields.forEach((item) => {
      console.warn(`Validation failed for field: ${item.name}, reason: ${item.message}`);
    });
  }
};

// Method to handle form submission
const handleSubmit = async () => {
  if (!form.value.account || !form.value.password) {
    MessagePlugin.warning('缺失必填项');
    return;
  }
  try {
    // 在这里将布尔值转换为数值
    const formData = {
      ...form.value,
      enable: form.value.enable ? 1 : 0 // 根据布尔值转换为 1 或 0
    };
    console.log('Form data:', formData);
    const response = await SysAddUser(formData);
    if (response.code === 200) {
      MessagePlugin.success('添加用户成功');
      if (props.onRefresh) {
        props.onRefresh();
      }
    }
    resetFormData();
  } catch (error) {
    console.error('Error submitting form:', error);
  } finally {
    visible.value = false;
  }
};

// Reset form data when the dialog is closed or canceled
const resetFormData = () => {
  form.value = { ...initialFormData };
};

const onCancel = (context) => {
  console.log('Canceled:', context);
  visible.value = false;
  resetFormData();
};

const onEscKeydown = (context) => {
  console.log('ESC pressed:', context);
};

const onCloseBtnClick = (context) => {
  console.log('Closed with button:', context);
  visible.value = false;
  resetFormData();
};

const onOverlayClick = (context) => {
  console.log('Overlay clicked:', context);
  visible.value = false;
  resetFormData();
};

// Method to expose opening functionality to parent component
const onOwnerClick = () => {
  visible.value = true;
};

// Watch for dialog opening
watch(visible, async (newVal) => {
  if (newVal) {
    setTimeout(() => {
      formRef.value.validate();
    }, 0);
  }
});

defineExpose({
  onOwnerClick,
});
</script>

<style scoped>
/* Add any additional styles if needed */
</style>
