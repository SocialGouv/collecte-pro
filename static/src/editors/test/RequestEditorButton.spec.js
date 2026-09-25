import { vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import { getField, updateField } from 'vuex-map-fields'
import flushPromises from 'flush-promises'

import axios from 'axios'
import RequestEditorButton from '../RequestEditorButton'
import { createStore } from 'vuex'
vi.mock('axios')

describe('RequestEditorButton.vue', () => {
  let store
  const user = { id: 123 }
  beforeEach(() => {
    store = createStore({
      state: {
        sessionUser: user,
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
    const questionnaire = {
      id: 345,
    }
    const wrapper = shallowMount(RequestEditorButton,
      {
        global: {
          plugins: [store],
        },
        props: {
          questionnaire,
        },
      })
    expect(wrapper.exists()).toBeTruthy()
  })

  describe('if questionnaire has no editor', () => {
    let wrapper
    let questionnaire
    let mockWindow
    beforeEach(() => {
      axios.put.mockResolvedValue({})
      mockWindow = {
        location: {
          assign: vi.fn(() => {}),
        },
      }

      questionnaire = {
        id: 345,
      }
      wrapper = shallowMount(RequestEditorButton,
        {
          global: {
            plugins: [store],
          },
          props: {
            questionnaire,
            window: mockWindow,
          },
        })
    })

    test('clicking "Obtain rights" calls the api to take rights', () => {
      wrapper.find('.obtain-rights-button').trigger('click')

      expect(axios.put).toHaveBeenCalledWith(
        '/api/questionnaire/' + questionnaire.id + '/changer-redacteur/',
        { editor: user.id })
    })

    test('clicking "Obtain rights" redirects to non-editable page', async () => {
      wrapper.find('.obtain-rights-button').trigger('click')

      await flushPromises()

      expect(mockWindow.location.assign).toHaveBeenCalledWith(expect.stringContaining('modifier'))
      expect(mockWindow.location.assign).toHaveBeenCalledWith(expect.stringContaining('questionnaire'))
      expect(mockWindow.location.assign).toHaveBeenCalledWith(expect.stringContaining('' + questionnaire.id))
    })
  })
})
