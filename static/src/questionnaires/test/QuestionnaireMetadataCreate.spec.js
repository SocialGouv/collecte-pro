import { mount } from '@vue/test-utils'
import { getField, updateField } from 'vuex-map-fields'
import QuestionnaireMetadataCreate from '../QuestionnaireMetadataCreate.vue'
import { createStore } from 'vuex'

describe('QuestionnaireMetadataCreate.vue', () => {
  let store
  const currentQuestionnaire = {
    id: 12345,
    description: '',
    questionnaire_files: [],
    title: '',
  }
  beforeEach(() => {
    store = createStore({
      state: {
        currentQuestionnaire: currentQuestionnaire,
      },
      getters: {
        getField,
      },
      mutations: {
        updateField,
        updateCurrentQuestionnaireField(state, { field, value }) {
          state.currentQuestionnaire[field] = value
        },
      },
    })
  })

  test('is a Vue instance', () => {
    const wrapper = mount(QuestionnaireMetadataCreate, {
      props: {
        questionnaire: currentQuestionnaire,
        questionnaireNumbering: 1,
      },
      global: {
        plugins: [store],
      },
    })
    expect(wrapper.exists()).toBeTruthy()
  })
})
