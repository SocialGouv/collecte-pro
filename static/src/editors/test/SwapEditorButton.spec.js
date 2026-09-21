import { shallowMount } from '@vue/test-utils'

import EventBus from '../../events'
import SwapEditorButton from '../SwapEditorButton'

describe('SwapEditorButton.vue', () => {
  let wrapper
  let mockModal

  beforeEach(() => {
    mockModal = jest.fn()
    global.$ = jest.fn(() => ({
      modal: mockModal,
    }))

    wrapper = shallowMount(SwapEditorButton, {
      props: {
        controlId: 5678,
      },
    })
  })

  afterEach(() => {
    wrapper.unmount()
    delete global.$
  })

  test('is a Vue instance', () => {
    expect(wrapper.exists()).toBeTruthy()
  })

  test('clicking the swap button emits a save-draft event', () => {
    wrapper.find('button').trigger('click')

    expect(wrapper.emitted('save-draft')).toBeTruthy()
    expect(wrapper.emitted('save-draft')).toHaveLength(1)
  })

  // Regression test for a bug introduced during the Vue 2 -> 3 migration : the parent
  // (QuestionnaireCreate.vue) emits 'show-swap-editor-modal' on the shared EventBus once the
  // draft is saved, and this component used to listen on `window.$parent.$on(...)`, which never
  // works (window has no $parent, and Vue 3 instances no longer have $on/$off/$once at all).
  test('shows the swap editor modal when EventBus emits show-swap-editor-modal', async () => {
    const questionnaireId = 1234

    EventBus.$emit('show-swap-editor-modal', questionnaireId)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.questionnaireId).toBe(questionnaireId)
    expect(global.$).toHaveBeenCalledWith('#swapEditorModal')
    expect(mockModal).toHaveBeenCalledWith('show')
  })

  test('stops listening to EventBus after being unmounted', async () => {
    wrapper.unmount()
    mockModal.mockClear()

    EventBus.$emit('show-swap-editor-modal', 9999)
    await new Promise(resolve => setTimeout(resolve, 0))

    expect(mockModal).not.toHaveBeenCalled()
  })
})
