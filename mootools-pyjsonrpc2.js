/*
 * Plugin for mootools
 * Author: Nikita Kuznetcov
 * Thx Constantin Slednev
 * 2010
 * license type: GPL
 *

Example usage:

//by form
$("form").jsonrpc('check_username');

//custom post element
new Request.JSONRPC({name:'check_username',url:'/json'}).post($("form"))

//custom send object
new Request.JSONRPC({name:'check_username',url:'/json'}).send({username:"admin"})

var creater = function (text) {
    return function (){
        console.log(text,arguments)
        }
    };
$("form").set('jsonrpc',{name:'check_username', url:'/json',
    {
        onFailure: creater("fail"),
        onSuccess: creater("success"),
    }
}).jsonrpc()
*/

Element.Properties.jsonrpc = {
    set: function(options){
         var jsonrpc = this.retrieve('jsonrpc');
         if (jsonrpc) jsonrpc.cancel();
         return this.eliminate('jsonrpc').store('jsonrpc:options', $extend(
                     {
                        data: this, 
                        link: 'cancel', 
                        method: this.get('method') || 'post', 
                        url: this.get('action')
                    }, options));
    },
    get: function(options){
         if (options || !this.retrieve('jsonrpc')){
             if (options || !this.retrieve('jsonrpc:options')) this.set('jsonrpc', options);
             this.store('jsonrpc', new Request.JSONRPC(this.retrieve('jsonrpc:options')));
         }
         return this.retrieve('jsonrpc');
    }

};

Element.implement({
    toJSON: function(){
        var json = {};
        this.getElements('input, select, textarea', true).each(function(el){
            if (!el.name || el.disabled || el.type == 'submit' || el.type == 'reset' || el.type == 'file') return;
            var value = (el.tagName.toLowerCase() == 'select') ? Element.getSelected(el).map(function(opt){
                return opt.value;
            }) : ((el.type == 'radio' || el.type == 'checkbox') && !el.checked) ? null : el.value;
            $splat(value).each(function(val){
                if (typeof val != 'undefined') json[el.name]=val;
            });
        });
        return json;
    },

    jsonrpc: function(name,url){
        var sender = this.get('jsonrpc');
        sender.headers.extend({'Accept': 'application/json', 'X-Request': 'JSONRPC','Content-Type':'application/json'});
//        new Request.JSONRPC($extend({name:name||sender.options.name,url:url||sender.options.url},sender)).send($(this))
        sender.send({
                    name:name||sender.options.name,
                    method:sender.options.method || 'post',
                    url:url||sender.options.url,
                    data:$(this)
                });
        return this;
    }
});
//    { "method": "check_username", "params": ["Hello JSON-RPC"], "id": 122}
Request.JSONRPC = new Class({

    Extends: Request,
    initialize: function(options){
        this.parent(options);
        this.headers.extend({'Accept': 'application/json', 'X-Request': 'JSONRPC','Content-Type':'application/json'});
        this._send = this.send;
        this.send =  function (args) {
            if($type(args) == 'element' || !$defined(args.method))  args={method:'post',data:args}
            var data = args.data;
            switch ($type(data)) {
                case 'element': 
                    data = document.id(data).toJSON(); 
                    break;
            }
            args.data = JSON.encode({'method':args.name||this.options.name,'params':data,'id':null})
            console.log("RPC "+(args.url||this.options.url)+" send "+args.data);
            this._send.apply(this,[args])

        }
    },

    success: function(text){
        var json = JSON.decode(text, this.options.secure);
        var isError;
        if($defined(json["result"])) {
            isError=false;
            this.response.json=json["result"];
        } else {
            isError=true;
            this.response.json=json["error"];
        }
        this.onSuccess(this.response.json,isError);
    }
});
