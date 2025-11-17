// EventBus.ts
import mitt from 'mitt';

type Events = {
    [key: string]: any; // tu peux préciser des types si tu veux
};

const EventBus = mitt<Events>();

export default EventBus;
