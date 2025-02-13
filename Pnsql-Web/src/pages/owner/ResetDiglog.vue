<template>
  <t-space>
    <t-dialog
      v-model:visible="visible"
      header="更改密码"
      width="40%"
      :confirm-on-enter="true"
      :on-cancel="onCancel"
      :on-esc-keydown="onEscKeydown"
      :on-close-btn-click="onCloseBtnClick"
      :on-overlay-click="onOverlayClick"
      :on-close="close"
    >
      <div style="text-align: center; overflow: hidden">
        <t-space direction="vertical" size="large" style="width: 95%; margin: 0 auto">
          <t-form ref="formRef" :data="form" :rules="rules" @validate="onValidate">
            <t-form-item label="新密码" name="newPassword">
              <t-input
                v-model="form.newPassword"
                placeholder="新密码"
                style="margin-bottom: 8px"
                size="large"
              />
            </t-form-item>

            <t-form-item label="确认密码" name="confirmPassword">
              <t-input
                v-model="form.confirmPassword"
                type="password"
                placeholder="确认密码"
                style="margin-bottom: 8px"
                size="large"
              />
            </t-form-item>
          </t-form>
        </t-space>
      </div>

      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%">
          <div style="color: red; font-weight: bold; display: flex; align-items: center">
            <t-icon v-if="errorMessage" name="warning-circle" style="margin-right: 4px" />
            <span>{{ errorMessage }}</span>
          </div>
          <div>
            <t-button theme="default" @click="onCancel">取消</t-button>
            <t-button theme="primary" @click="onConfirm">确认</t-button>
          </div>
        </div>
      </template>
    </t-dialog>
  </t-space>
</template>

<script setup>
import { ref } from 'vue';
import {SysUptPassword} from '@/api/services/sysUser';
import {MessagePlugin} from "tdesign-vue-next";
const visible = ref(false);
const formRef = ref(null);
const errorMessage = ref('');
const rowID = ref('');

const form = ref({
  newPassword: '',
  confirmPassword: '',
});

const rules = {
  newPassword: [
    {required: true, message: '密码不能为空', type: 'warning'},
    {
      validator: (value) => value.length >= 6,
      message: '密码长度至少为6位',
      type: 'warning',
    },
  ],
  confirmPassword: [
    {required: true, message: '请确认密码', type: 'warning'},
    {
      validator: (value) => value === form.value.newPassword,
      message: '两次输入的密码不一致',
      type: 'warning',
    },
  ],
};

const onResetClick = (id) => {
  visible.value = true;
  rowID.value = id;
  errorMessage.value = ''; // 清空错误信息
};

const onConfirm = () => {
  // 手动验证以避免表单提交不合法数据
  if (form.value.newPassword.length < 6) {
    return;
  }
  if (form.value.confirmPassword !== form.value.newPassword) {
    return;
  }

  formRef.value
    .validate()
    .then(async () => {
      const response = await SysUptPassword(rowID.value, form.value.newPassword);
      if (response.code === 200) {
        MessagePlugin.success('重置成功');
      }
      visible.value = false;
      resetFormData();
    })
    .catch((invalidFields) => {
      if (invalidFields) {
        errorMessage.value = Object.values(invalidFields).flat()[0].message;
      }
    });
};

const onValidate = ({ errorFields }) => {
  if (errorFields && errorFields.length > 0) {
    errorFields.forEach((item) => {
      console.warn(`Validation failed for field: ${item.name}, reason: ${item.message}`);
    });
  }
};

const onCancel = () => {
  visible.value = false; // 关闭对话框
  resetFormData();
};

const close = () => {
  errorMessage.value = ''; // 清空错误信息
  resetFormData();
};

const onEscKeydown = () => {
};

const onCloseBtnClick = () => {
};

const onOverlayClick = () => {
};

const resetFormData = () => {
  form.value = {
    newPassword: '',
    confirmPassword: '',
  };
};

defineExpose({
  onResetClick,
});
</script>
