<template>
    <div id="app">
        <vue-ads-table
            :columns="columns"
            :rows="rows"
        >
            <!-- Will be applied on the name column for the rows with an _id of tiger -->
            <template slot="name" slot-scope="props">{{ props.row.name }}</template>
            <template slot="dateDepot" slot-scope="props">{{ props.row.dateDepot }}</template>
            <template slot="repondant" slot-scope="props">{{ props.row.redacteur }}</template>
            <template slot="no-rows">Pas de résultats</template>
            <template slot="toggle-children-icon" slot-scope="props"> [{{ props.expanded ? '-' : '+' }}] </template>
        </vue-ads-table>
    </div>
</template>

<script>
import '../../../node_modules/@fortawesome/fontawesome-free/css/all.min.css';
import '../../../node_modules/vue-ads-table-tree/dist/vue-ads-table-tree.css';
import { VueAdsTable } from 'vue-ads-table-tree';

export default {
    components: {
        VueAdsTable,
    },

    data () {
        let rows = [
            {
                name: 'Questionnaire 1',
                dateDepot: '20/03/2022',
                redacteur: 'Alexandre MORIN',
                _hasChildren: false,
            },
            {
                name: 'Questionnaire 2',
                dateDepot: '21/03/2022',
                redacteur: 'Alexandre MORIN',
                _showChildren: true,
                _children: [
                    {
                        name: 'Question 2.1',
                        dateDepot: '22/03/2022',
                        redacteur: 'Alexandre MORIN',
                        _showChildren: true,
                        _children: [
                            {
                                name: 'Fichier 2.1.1',
                                dateDepot: '22/03/2022',
                                redacteur: 'Thomas BOUCHET',
                            },
                        ],
                    },
                ],
            },
        ];
        
        rows.length = 4;
        
        let columns = [
            {
                property: 'name',
                title: 'Nom du document',
            },
            {
                property: 'dateDepot',
                title: 'Date de dépot',
            },
            {
                property: 'repondant',
                title: 'Répondant',
            },
        ];
        
        let classes = {
            group: {
                'vue-ads-font-bold': true,
                'vue-ads-border-b': true,
                'vue-ads-italic': true,
            },
            '0/all': {
                'vue-ads-py-3': true,
                'vue-ads-px-2': true,
            },
            'even/': {
                'vue-ads-bg-blue-lighter': true,
            },
            'odd/': {
                'vue-ads-bg-blue-lightest': true,
            },
            '0/': {
                'vue-ads-bg-blue-lighter': false,
                'vue-ads-bg-blue-dark': true,
                'vue-ads-text-white': false,
                'vue-ads-font-bold': true,
            },
            '1_/': {
                'hover:vue-ads-bg-red-lighter': true,
            },
            '1_/0': {
                'leftAlign': true
            }
        };

        return {
            rows,
            columns,
            classes,
            filter: '',
            start: 0,
            end: 2,
        };
    },
    
    methods: {

    },
};
</script>

<style>
    .leftAlign {
        text-align: left;
    }
</style>