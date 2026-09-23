import { vi } from 'vitest'
import assert from 'assert'
import axios from 'axios'
import { mount, shallowMount } from '@vue/test-utils'
import { getField, updateField } from 'vuex-map-fields'
import EventBus from '../../events'
import QuestionnaireCreate from '../QuestionnaireCreate.vue'
import { createStore } from 'vuex'
import { loadStatuses } from '../../store'
import flushPromises from 'flush-promises'

vi.mock('axios')

const QuestionnaireCreateForTest = {
  ...QuestionnaireCreate,
  mounted() {
    if (typeof this.questionnaireId === 'undefined') {
      this.loadNewQuestionnaire()
    } else {
      this.loadExistingQuestionnaire()
    }
    if (this.controlId === undefined && this.questionnaireId === undefined) {
      throw Error('QuestionnaireCreate needs a controlId or a questionnaireId')
    }
  },
}

describe('QuestionnaireCreate.vue', () => {
  let store
  let jqueryMock

  beforeEach(() => {
    vi.resetModules()
    vi.clearAllMocks()

    jqueryMock = {
      addClass: vi.fn(),
      css: vi.fn(),
      height: vi.fn(() => 0),
      modal: vi.fn(),
      removeClass: vi.fn(),
      scrollTop: vi.fn(() => 0),
      scroll: vi.fn(),
      resize: vi.fn(),
    }
    global.$ = vi.fn(() => jqueryMock)

    store = createStore({
      state: {
        controls: [],
        controlsLoadStatus: loadStatuses.LOADING,
        currentQuestionnaire: {},
      },
      getters: {
        getField,
      },
      mutations: {
        updateField,
        setCurrentQuestionnaire(state, questionnaire) {
          state.currentQuestionnaire = questionnaire
        },
        updateCurrentQuestionnaireField(state, { field, value }) {
          if (!state.currentQuestionnaire) {
            state.currentQuestionnaire = {}
          }
          state.currentQuestionnaire[field] = value
        },
        updateControls(state, controls) {
          state.controls = controls
        },
        updateControlsLoadStatus(state, newStatus) {
          state.controlsLoadStatus = newStatus
        },
      },
    })
  })

  afterEach(() => {
    // If we removed error output in previous test, set it back for next test.
    if (console.error.mockRestore) {
      console.error.mockRestore()
    }
    delete global.$
  })

  const mockLoadedQuestionnaire = (controlId, questionnaire) => {
    axios.get.mockResolvedValue({
      data: [{
        id: controlId,
        questionnaires: [{
          ...questionnaire,
          description: questionnaire.description || 'description',
          questionnaire_files: questionnaire.questionnaire_files || [],
          themes: questionnaire.themes || [],
        }],
      }],
    })
  }

  test('is a Vue instance', () => {
    const wrapper = shallowMount(
      QuestionnaireCreateForTest,
      {
        props: {
          controlId: 1,
        },
        global: {
          plugins: [store],
        },
      })
    expect(wrapper.exists()).toBeTruthy()
  })

  test('crashes without a controlId or questionnaireId', () => {
    // Remove error output, since we expect an error. Avoids clutter in test log.
    vi.spyOn(console, 'error')
    console.error.mockImplementation(() => { })

    expect(() => {
      shallowMount(
        QuestionnaireCreateForTest,
        {
          props: {
            // no controlId or questionnaireId
          },
          global: {
            plugins: [store],
          },
        })
    }).toThrow()
  })

  describe('create new questionnaire', () => {
    test('sets up without crashing', () => {
      expect(() => {
        shallowMount(
          QuestionnaireCreateForTest,
          {
            props: {
              controlId: 1,
            },
            global: {
              plugins: [store],
            },
          })
      }).not.toThrow()
    })

    test('sets currrentQuestionnaire into store', async () => {
      const controlId = 1

      shallowMount(
        QuestionnaireCreateForTest,
        {
          props: {
            controlId: 1,
          },
          global: {
            plugins: [store],
          },
        })

      store.commit('updateControls', [{ id: controlId }])
      store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)

      await flushPromises()

      expect(store.state.currentQuestionnaire.control).toBe(controlId)
      expect(store.state.currentQuestionnaire.description).not.toBe('')
    })

    test('moves to first step of wizard', async () => {
      const controlId = 1

      const wrapper = shallowMount(
        QuestionnaireCreateForTest,
        {
          props: {
            controlId: 1,
          },
          global: {
            plugins: [store],
          },
        })

      store.commit('updateControls', [{ id: controlId }])
      store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)

      await flushPromises()

      expect(wrapper.vm.state).toBe(1)

      assert(wrapper.find('#questionnaire-metadata-create').isVisible())
      assert(!wrapper.find('#questionnaire-body-create').isVisible())
      assert(!wrapper.find('#questionnaire-preview').isVisible())

      assert(wrapper.findComponent('#wizard').props().activeStepNumber === 1)
    })
  })

  describe('update existing questionnaire', () => {
    test('sets up without crashing', () => {
      const questionnaireId = 1
      const controlId = 2
      const questionnaire = {
        control: controlId,
        id: questionnaireId,
        is_draft: true,
      }

      mockLoadedQuestionnaire(controlId, questionnaire)
      store.commit('updateControls', [{
        id: controlId,
        questionnaires: [questionnaire],
      }])
      store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)

      expect(() => {
        shallowMount(
          QuestionnaireCreateForTest,
          {
            props: {
              controlId,
              questionnaireId,
            },
            global: {
              plugins: [store],
            },
          })
      }).not.toThrow()
    })

    test('sets currrentQuestionnaire into store', async () => {
      const questionnaireId = 1234
      const controlId = 5678
      const questionnaire = {
        control: controlId,
        id: questionnaireId,
        is_draft: true,
      }

      mockLoadedQuestionnaire(controlId, questionnaire)
      store.commit('updateControls', [{
        id: controlId,
        questionnaires: [
          questionnaire,
        ],
      }])
      store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)

      shallowMount(
        QuestionnaireCreateForTest,
        {
          props: {
            controlId,
            questionnaireId,
          },
          global: {
            plugins: [store],
          },
        })

      await flushPromises()

      expect(store.state.currentQuestionnaire).toEqual(questionnaire)
    })

    describe('displays error', () => {
      test('if cannot get questionnaire from store', async () => {
        vi.spyOn(console, 'error')
        console.error.mockImplementation(() => { })

        const questionnaireId = 1234
        const controlId = 5678
        const TestQuestionnaireCreate = {
          ...QuestionnaireCreateForTest,
          mounted() { },
        }

        const wrapper = shallowMount(
          TestQuestionnaireCreate,
          {
            props: {
              controlId,
              questionnaireId,
            },
            global: {
              plugins: [store],
            },
          })

        expect(() => {
          wrapper.vm.$options.watch.controlsLoadStatus.call(wrapper.vm, loadStatuses.ERROR)
        }).toThrow('Store status is ERROR. Not loading questionnaire.')

        await flushPromises()

        expect(store.state.currentQuestionnaire).toEqual({})

        assert(wrapper.vm.errorMessage !== '')
        assert(wrapper.vm.hasErrors)
        assert(wrapper.find('#questionnaire-create-error').exists())

        // The wizard steps are removed from the DOM entirely (v-if) while there's a
        // load error, rather than merely hidden.
        assert(!wrapper.find('#questionnaire-metadata-create').exists())
        assert(!wrapper.find('#questionnaire-body-create').exists())
        assert(!wrapper.find('#questionnaire-preview').exists())
      })

      test('if questionnaire is not a draft', async () => {
        vi.spyOn(console, 'error')
        console.error.mockImplementation(() => { })

        const questionnaireId = 1234
        const controlId = 5678
        const questionnaire = {
          control: controlId,
          id: questionnaireId,
          is_draft: false,
        }

        mockLoadedQuestionnaire(controlId, questionnaire)
        store.commit('updateControls', [{
          id: controlId,
          questionnaires: [
            questionnaire,
          ],
        }])
        store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)

        const TestQuestionnaireCreate = {
          ...QuestionnaireCreateForTest,
          mounted() { },
        }

        const wrapper = shallowMount(
          TestQuestionnaireCreate,
          {
            props: {
              controlId,
              questionnaireId,
            },
            global: {
              plugins: [store],
            },
          })

        await expect(wrapper.vm.loadExistingQuestionnaire()).rejects.toThrow(
          'Questionnaire ' + questionnaireId + ' is not a draft, you cannot edit it')

        expect(store.state.currentQuestionnaire).toEqual({})

        assert(wrapper.vm.errorMessage !== '')
        assert(wrapper.vm.hasErrors)
        assert(wrapper.find('#questionnaire-create-error').exists())

        // The wizard steps are removed from the DOM entirely (v-if) while there's a
        // load error, rather than merely hidden.
        assert(!wrapper.find('#questionnaire-metadata-create').exists())
        assert(!wrapper.find('#questionnaire-body-create').exists())
        assert(!wrapper.find('#questionnaire-preview').exists())
      })
    })

    test('moves to first step of wizard', async () => {
      const questionnaireId = 1234
      const controlId = 5678
      const questionnaire = {
        control: controlId,
        id: questionnaireId,
        is_draft: true,
      }

      mockLoadedQuestionnaire(controlId, questionnaire)
      store.commit('updateControls', [{
        id: controlId,
        questionnaires: [
          questionnaire,
        ],
      }])
      store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)

      const wrapper = shallowMount(
        QuestionnaireCreateForTest,
        {
          props: {
            controlId,
            questionnaireId,
          },
          global: {
            plugins: [store],
          },
        })

      await flushPromises()

      expect(wrapper.vm.state).toBe(1)

      assert(wrapper.find('#questionnaire-metadata-create').isVisible())
      assert(!wrapper.find('#questionnaire-body-create').isVisible())
      assert(!wrapper.find('#questionnaire-preview').isVisible())

      assert(wrapper.findComponent('#wizard').props().activeStepNumber === 1)
    })
  })

  describe('Publishing flow', () => {
    let wrapper
    let questionnaire
    beforeEach(async () => {
      // The publishing UI now lives in PublishFlow.vue -> ModalFlow.vue (a generic 3-modal
      // "confirm / wait / success" flow), driven by real jQuery/Bootstrap `.modal()` calls
      // rather than component-level v-if/v-show. Make the jQuery mock actually toggle the
      // "show" class on the target element (like real Bootstrap would), so tests can observe
      // which modal is currently shown, and support `.on(...)` which ModalFlow calls.
      global.$ = vi.fn((el) => ({
        on: vi.fn(),
        modal: vi.fn((action) => {
          if (el && el.classList) {
            if (action === 'show') el.classList.add('show')
            else if (action === 'hide') el.classList.remove('show')
          }
        }),
        addClass: vi.fn(),
        removeClass: vi.fn(),
        css: vi.fn(),
        height: vi.fn(() => 0),
        scrollTop: vi.fn(() => 0),
        scroll: vi.fn(),
        resize: vi.fn(),
      }))

      // Setup component to load existing questionnaire
      const questionnaireId = 1234
      const controlId = 5678
      questionnaire = {
        control: controlId,
        id: questionnaireId,
        is_draft: true,
      }

      mockLoadedQuestionnaire(controlId, questionnaire)
      store.commit('updateControls', [{
        id: controlId,
        questionnaires: [
          questionnaire,
        ],
      }])
      store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)
      // PublishFlow reads store.state.config for the support email / env name / site url.
      store.state.config = {
        env_name: 'test',
        support_team_email: 'support@example.com',
        site_url: 'http://localhost',
      }

      wrapper = mount(
        QuestionnaireCreateForTest,
        {
          props: {
            controlId,
            questionnaireId,
          },
          global: {
            plugins: [store],
            // Only PublishFlow (and its ModalFlow/EmptyModal internals) need to be really
            // rendered for these tests ; stub everything else, like shallowMount would.
            stubs: {
              Breadcrumbs: true,
              SwapEditorButton: true,
              Wizard: true,
              QuestionnaireMetadataCreate: true,
              QuestionnaireBodyCreate: true,
              QuestionnairePreview: true,
            },
          },
        })

      await flushPromises()

      // Move to state 3 : ready to publish
      wrapper.vm.state = 3
      await wrapper.vm.$nextTick()
    })

    // ModalFlow always renders its 3 modals (confirm / wait / success) in this order.
    const confirmModal = () => wrapper.findAll('.modal')[0]
    const waitingModal = () => wrapper.findAll('.modal')[1]
    const successModal = () => wrapper.findAll('.modal')[2]
    const modalFlowVm = () => wrapper.findComponent({ name: 'ConfirmModalWithWait' }).vm

    test('Displays the questionnaire-preview component', () => {
      expect(wrapper.find('#questionnaire-metadata-create').isVisible()).toBeFalsy()
      expect(wrapper.find('#questionnaire-body-create').isVisible()).toBeFalsy()
      expect(wrapper.find('#questionnaire-preview').isVisible()).toBeTruthy()
    })

    test('shows the confirm modal when Publish button is clicked', async () => {
      await wrapper.find('#publishButton').trigger('click')

      expect(confirmModal().classes()).toContain('show')
    })

    test('shows the waiting modal when publishing is confirmed', async () => {
      await wrapper.find('#publishButton').trigger('click')
      await confirmModal().find('form').trigger('submit')

      expect(waitingModal().classes()).toContain('show')
    })

    test('calls publish api when publishing is confirmed', async () => {
      await wrapper.find('#publishButton').trigger('click')
      await confirmModal().find('form').trigger('submit')

      // PUT is called, because it's an update of an existing questionnaire.
      expect(axios.put).toHaveBeenCalledWith(
        '/api/questionnaire/' + questionnaire.id + '/',
        questionnaire)
    })

    test('shows success modal when publish happened successfully', async () => {
      // Mock out axios to return with success.
      axios.put.mockResolvedValue({})

      await wrapper.find('#publishButton').trigger('click')
      await confirmModal().find('form').trigger('submit')

      // The flow waits a minimum display time before showing the success modal.
      await new Promise((resolve) => setTimeout(resolve, 2100))
      await flushPromises()

      expect(successModal().classes()).toContain('show')
    }, 8000)

    test('displays errors when publish api returned errors', async () => {
      vi.spyOn(console, 'error')
      console.error.mockImplementation(() => { })

      // Mock axios to return publish error
      const error = { error: 'I am not happpyyyy', details: ['stuff', 'more stuff'] }
      axios.put.mockRejectedValue(error)

      await wrapper.find('#publishButton').trigger('click')
      await confirmModal().find('form').trigger('submit')
      // Resolve all promises
      await flushPromises()

      expect(modalFlowVm().error).toEqual(error)

      // Intermediate modal is gone
      expect(waitingModal().classes()).not.toContain('show')
      // Success modal not displayed
      expect(successModal().classes()).not.toContain('show')
      // Initial modal is back
      expect(confirmModal().classes()).toContain('show')
    })
  })

  describe('Navigation', () => {
    let wrapper
    const controlId = 1
    let mockWindow
    beforeEach(() => {
      mockWindow = {
        location: {
          href: '',
        },
      }
      wrapper = shallowMount(
        QuestionnaireCreateForTest,
        {
          props: {
            controlId,
            window: mockWindow,
          },
          global: {
            plugins: [store],
          },
        })
      store.commit('updateControls', [{ id: controlId }])
      store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)
    })

    test('Saves draft before returning home', async () => {
      // Spy on form validation to make it pass
      vi.spyOn(wrapper.vm, 'validateCurrentForm')
      wrapper.vm.validateCurrentForm.mockImplementation(() => true)
      // Mock axios to return the questionnaire it got in argument
      axios.post.mockImplementation((url, payload) => {
        return Promise.resolve({ data: payload })
      })
      await flushPromises()

      wrapper.find('#go-home-button').trigger('click')
      await flushPromises()
      // goHome() redirects after a short delay (so the user sees the "loading" state on the
      // button they clicked), so wait for it here.
      await new Promise((resolve) => setTimeout(resolve, 600))

      expect(wrapper.vm.validateCurrentForm).toHaveBeenCalled()
      expect(axios.post).toHaveBeenCalledWith(
        '/api/questionnaire/',
        expect.any(Object))
      expect(mockWindow.location.href).not.toBe('')
    })

    test('If draft save fails, return home anyway', async () => {
      // The component intentionally logs the failure via console.error; silence it for this
      // test only so the expected error path doesn't pollute the test output.
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => { })

      try {
        // Spy on form validation to make it pass
        vi.spyOn(wrapper.vm, 'validateCurrentForm')
        wrapper.vm.validateCurrentForm.mockImplementation(() => true)
        // Mock axios to fail save
        axios.post.mockRejectedValue({})
        await flushPromises()

        wrapper.find('#go-home-button').trigger('click')
        await flushPromises()
        // goHome() redirects after a short delay (so the user sees the "loading" state on the
        // button they clicked), so wait for it here.
        await new Promise((resolve) => setTimeout(resolve, 600))

        expect(wrapper.vm.validateCurrentForm).toHaveBeenCalled()
        expect(axios.post).toHaveBeenCalledWith(
          '/api/questionnaire/',
          expect.any(Object))
        expect(mockWindow.location.href).not.toBe('')
      } finally {
        consoleErrorSpy.mockRestore()
      }
    })

    test('If form validation fails, don\'t save and don\'t go home', async () => {
      // Spy on form validation to make it fail
      vi.spyOn(wrapper.vm, 'validateCurrentForm')
      wrapper.vm.validateCurrentForm.mockImplementation(() => false)
      await flushPromises()

      wrapper.find('#go-home-button').trigger('click')
      await flushPromises()

      expect(wrapper.vm.validateCurrentForm).toHaveBeenCalled()
      expect(axios.post).not.toHaveBeenCalled()
      expect(mockWindow.location.href).toBe('')
    })
    // Todo : test the navigation : back, next
  })

  // Regression test for a bug introduced during the Vue 2 -> 3 migration : SwapEditorButton used
  // to listen via `window.$parent.$on(...)`, which never actually worked in Vue 3 (instances no
  // longer have $on/$off, and window has no $parent). The communication now goes through the
  // shared EventBus instead.
  describe('swapEditor flow', () => {
    let wrapper
    const controlId = 5678
    const questionnaireId = 999

    beforeEach(() => {
      const questionnaire = {
        control: controlId,
        id: questionnaireId,
        is_draft: true,
      }
      mockLoadedQuestionnaire(controlId, questionnaire)
      store.commit('updateControls', [{
        id: controlId,
        questionnaires: [questionnaire],
      }])
      store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)

      wrapper = shallowMount(
        QuestionnaireCreateForTest,
        {
          props: {
            controlId,
            questionnaireId,
            controlHasMultipleInspectors: true,
          },
          global: {
            plugins: [store],
          },
        })
    })

    test('saveDraftAndSwapEditor saves the draft then emits show-swap-editor-modal on the EventBus',
      async () => {
        await flushPromises()

        const eventBusListener = vi.fn()
        EventBus.$on('show-swap-editor-modal', eventBusListener)

        vi.spyOn(wrapper.vm, 'validateCurrentForm').mockImplementation(() => true)
        axios.put.mockImplementation((url, payload) => {
          return Promise.resolve({ data: payload })
        })

        wrapper.vm.saveDraftAndSwapEditor()
        await flushPromises()

        expect(axios.put).toHaveBeenCalledWith(
          '/api/questionnaire/' + questionnaireId + '/',
          expect.any(Object))
        expect(eventBusListener).toHaveBeenCalledWith(questionnaireId)

        EventBus.$off('show-swap-editor-modal', eventBusListener)
      })

    test('does not emit show-swap-editor-modal if form validation fails', async () => {
      await flushPromises()

      const eventBusListener = vi.fn()
      EventBus.$on('show-swap-editor-modal', eventBusListener)

      vi.spyOn(wrapper.vm, 'validateCurrentForm').mockImplementation(() => false)

      wrapper.vm.saveDraftAndSwapEditor()
      await flushPromises()

      expect(axios.put).not.toHaveBeenCalled()
      expect(eventBusListener).not.toHaveBeenCalled()

      EventBus.$off('show-swap-editor-modal', eventBusListener)
    })
  })
  // Todo : test the save button
})
