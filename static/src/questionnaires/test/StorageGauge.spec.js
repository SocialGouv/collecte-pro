import { mount } from '@vue/test-utils'
import StorageGauge from '../StorageGauge.vue'

const GO_IN_BYTES = 1024 * 1024 * 1024
const MO_IN_BYTES = 1024 * 1024

describe('StorageGauge.vue', () => {
  test('is a Vue instance', () => {
    const wrapper = mount(StorageGauge, {
      props: { usedBytes: 0 },
    })
    expect(wrapper.exists()).toBeTruthy()
  })

  test('renders the full card by default (not compact)', () => {
    const wrapper = mount(StorageGauge, {
      props: { usedBytes: 0 },
    })
    expect(wrapper.find('.storage-gauge-compact').exists()).toBe(false)
    expect(wrapper.find('.card.storage-gauge').exists()).toBe(true)
    expect(wrapper.text()).toContain('Espace utilisé pour le dépôt de fichiers')
  })

  test('renders the compact variant when compact prop is set', () => {
    const wrapper = mount(StorageGauge, {
      props: { usedBytes: 0, compact: true },
    })
    expect(wrapper.find('.storage-gauge-compact').exists()).toBe(true)
    expect(wrapper.find('.card.storage-gauge').exists()).toBe(false)
  })

  test('formats sizes below 1 Go in Mo', () => {
    const wrapper = mount(StorageGauge, {
      props: { usedBytes: 50 * MO_IN_BYTES },
    })
    expect(wrapper.text()).toContain('50 Mo / 1 Go')
  })

  test('formats sizes at or above 1 Go in Go', () => {
    const wrapper = mount(StorageGauge, {
      props: { usedBytes: 1.5 * GO_IN_BYTES },
    })
    expect(wrapper.text()).toContain('1.50 Go / 1 Go')
  })

  test('computes 0% width and green color for no usage', () => {
    const wrapper = mount(StorageGauge, {
      props: { usedBytes: 0 },
    })
    const bar = wrapper.find('.progress-bar')
    expect(bar.attributes('style')).toContain('width: 0%')
    expect(bar.attributes('aria-valuenow')).toBe('0')
    expect(bar.classes()).toContain('bg-green')
  })

  test('uses bg-green-light between 75% and 90% usage', () => {
    const wrapper = mount(StorageGauge, {
      props: { usedBytes: 0.8 * GO_IN_BYTES },
    })
    const bar = wrapper.find('.progress-bar')
    expect(bar.classes()).toContain('bg-green-light')
  })

  test('uses bg-orange between 90% and 100% usage', () => {
    const wrapper = mount(StorageGauge, {
      props: { usedBytes: 0.95 * GO_IN_BYTES },
    })
    const bar = wrapper.find('.progress-bar')
    expect(bar.classes()).toContain('bg-orange')
  })

  test('uses bg-red and caps at 100% when usage reaches or exceeds quota', () => {
    const wrapper = mount(StorageGauge, {
      props: { usedBytes: 2 * GO_IN_BYTES },
    })
    const bar = wrapper.find('.progress-bar')
    expect(bar.classes()).toContain('bg-red')
    expect(bar.attributes('style')).toContain('width: 100%')
    expect(bar.attributes('aria-valuenow')).toBe('100')
  })
})
