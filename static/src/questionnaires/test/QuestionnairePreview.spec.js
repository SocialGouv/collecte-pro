import { shallowMount } from '@vue/test-utils'
import { getField, updateField } from 'vuex-map-fields'

import QuestionnairePreview from '../QuestionnairePreview.vue'
import QuestionnaireDetailForPreview from '../QuestionnaireDetailForPreview'
import { createStore } from 'vuex'

describe('QuestionnairePreview.vue', () => {
  let store
  const currentQuestionnaire = { id: 12345 }
  beforeEach(() => {
    store = createStore({
      state: {
        currentQuestionnaire,
      },
      getters: {
        getField,
      },
      mutations: {
        updateField,
      },
    })
  })

  test('is a Vue instance', () => {
    // shallowMount stubs out all children
    const wrapper = shallowMount(QuestionnairePreview, {
      global: {
        plugins: [store],
      },
    })
    expect(wrapper.exists()).toBeTruthy()
  })

  test('passes questionnaire to QuestionnaireDetailForPreview', () => {
    const wrapper = shallowMount(QuestionnairePreview, {
      global: {
        plugins: [store],
        stubs: {
          QuestionnaireDetailForPreview: true,
        },
      },
    })

    const child = wrapper.findComponent(QuestionnaireDetailForPreview)
    expect(child.exists()).toBe(true)
    expect(child.props().questionnaire).toEqual(currentQuestionnaire)
  })
})
