
Ext.define('ProtoUL.view.diagram.EntityAttributes', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.entityattributes',

    requires: [
        'Ext.grid.column.CheckColumn',
        'Ext.grid.column.Boolean',
        'Ext.grid.View'
    ],
	itemId: 'entityattributes',
    title: 'Attributes',
    store: 'EntityAttributeStore',

    initComponent: function() {
        var me = this;

		this.rowEditing = Ext.create('Ext.grid.plugin.RowEditing', {
	        clicksToMoveEditor: 1,
	        autoCancel: false
	    });
	    
    	this.plugins = [this.rowEditing];

		var storeDBTypes = Ext.create('ProtoUL.store.DBTypesStore');

        Ext.applyIf(me, {
            columns: [
                {
                    xtype: 'gridcolumn',
                    dataIndex: 'text',
                    text: 'Name',
		            editor: {
		                allowBlank: false
		            }
                },
                {
                    xtype: 'gridcolumn',
                    dataIndex: 'datatype',
                    text: 'Datatype',
                    width: 75,
		            editor: {
		            	xtype: 'combo',
			            store: storeDBTypes,
			            displayField: 'typeName',
			            valueField: 'typeID',
			            queryMode: 'local',
			            selectOnFocus: true,
			            triggerAction: 'all',
		                allowBlank: false
		            }
                },
                {
                    xtype: 'checkcolumn',
                    width: 35,
                    dataIndex: 'pk',
                    text: 'PK',
		            editor: {
		                xtype: 'checkbox',
		                cls: 'x-grid-checkheader-editor'
		            }
                },
                {
                    xtype: 'checkcolumn',
                    width: 35,
                    dataIndex: 'fk',
                    text: 'FK',
		            editor: {
		                xtype: 'checkbox',
		                cls: 'x-grid-checkheader-editor'
		            }
                },
                {
                    xtype: 'checkcolumn',
                    width: 55,
                    dataIndex: 'isRequired',
                    text: 'Required',
		            editor: {
		                xtype: 'checkbox',
		                cls: 'x-grid-checkheader-editor'
		            }
                },
                {
                    xtype: 'checkcolumn',
                    width: 35,
                    dataIndex: 'isNullable',
                    text: 'Null',
		            editor: {
		                xtype: 'checkbox',
		                cls: 'x-grid-checkheader-editor'
		            }
                }
            ]
        });

		this.dockedItems = [{
            xtype: 'toolbar',
            items: [{
                iconCls: 'icon-tableAdd',
                itemId: 'btAddAttribute',
                text: 'Add',
                action: 'addattribute'
            }, {
                iconCls: 'icon-tableDelete',
                itemId: 'btDeleteAttribute',
                text: 'Delete',
                action: 'deleteattribute'
            }]
        }];
        
        me.callParent(arguments);
    }

});