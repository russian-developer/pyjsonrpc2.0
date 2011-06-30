var jsonrpc = function(name,url){
        var sender = this.get('jsonrpc');
        sender.send({
                    name:name||sender.options.name,
                    method:sender.options.method || 'post',
                    url:url||sender.options.url,
                    data:$(this)
                });
        return this;
}

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
    toJSON: function(hidden){
        var hidden = hidden || false;
        var json = {};
        this.getElements('input, select, textarea', true).each(function(el){
            if (!el.name || el.disabled || el.type == 'submit' || el.type == 'reset' || el.type == 'file') return;
            if (!hidden && el.offsetHeight == 0 && el.type != 'hidden' ) return;
            var value = (el.tagName.toLowerCase() == 'select') ? Element.getSelected(el).map(function(opt){
                return opt.value;
            }) : ((el.type == 'radio' || el.type == 'checkbox') && !el.checked) ? null : (el.name.substring(el.name.length-2) == '[]') ? el.value : el.value;
            $splat(value).each(function(val){
                if ($type(val) != 'undefined') {
                    if (el.name.substring(el.name.length-2) == '[]') {
                        var name = el.name.substring(0, el.name.length-2)
                        if ($type(json[name]) != "array") {
                            json[name] = [];
                        }
                        json[name].push(val);
                    }
                    else {
                        if (!$type(json[el.name])) {
                            json[el.name]=val;
                        }
                        else {
                            if ($type(json[el.name]) != "array") {
                                oldval = json[el.name];
                                json[el.name] = [oldval];
                            }
                            json[el.name].push(val);
                        }
                    }
                }
            });
        });
        return json;
    },

    jsonrpc: jsonrpc
});
Request.JSONRPC = new Class({
    Extends: Request,
    options:{
        urlEncoded:false,
        method:'post'
    },
    initialize: function(options){
        this.parent(options || {});
        this.headers = $extend(this.headers,{'Accept': 'application/json', 'X-Request': 'JSONRPC','Content-Type':'application/json'});
        this._send = this.send;
        this.send =  function (args) {
            if(args.url) {
                var now = new Date();
                args['url'] = args['url'] + (args['url'].indexOf("?") > -1 ? "&" : "?") + "nocache=" + now.getMilliseconds() + now.getSeconds() + now.getMinutes();
            }
            if(!$defined(args) || $type(args) == 'element' || !$defined(args.method))  args={method:'post',data:args}
            var data = args.data;
            switch ($type(data)) {
                case 'element': 
                    data = document.id(data).toJSON(); 
                    break;
            }
            args.data = JSON.encode({'method':args.name||this.options.name,'params':data,'id':null})
            this._send.apply(this,[args])

        }
    },
    success: function(text){
        var json = JSON.decode(text, this.options.secure);
        if($defined(json["result"])) {
		    this.fireEvent('success', [json['result']]).callChain();
        } else {
		    this.fireEvent('error', [json['error'],json['data'] || []]).callChain();
        }
    }
});
