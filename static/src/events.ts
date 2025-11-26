// EventBus.ts
import mitt from 'mitt';

type Events = {
    [key: string]: any; // tu peux préciser des types si tu veux
};

const mittBus = mitt<Events>();

// Backwards-compatible wrapper exposing Vue2-style $on/$off/$emit
const EventBus = {
    $on: (type: string, handler: any) => mittBus.on(type, handler),
    $off: (type: string, handler?: any) => mittBus.off(type, handler),
    $emit: (type: string, event?: any) => mittBus.emit(type, event),
    on: mittBus.on,
    off: mittBus.off,
    emit: mittBus.emit,
}

export default EventBus;
