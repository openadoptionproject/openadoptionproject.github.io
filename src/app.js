(function(){
  var $=function(s,r){return (r||document).querySelector(s)}, $$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
  function store(k,v){try{if(v===undefined)return JSON.parse(localStorage.getItem(k)||'null');localStorage.setItem(k,JSON.stringify(v))}catch(e){return null}}

  // mobile menu
  var mb=$('.menu-btn'),nav=$('.nav');
  if(mb&&nav){mb.addEventListener('click',function(){var o=nav.classList.toggle('open');mb.setAttribute('aria-expanded',o?'true':'false')})}

  // episode library
  var list=$('#eplist');
  if(list){
    var rows=$$('li',list), q=$('#q'), chips=$$('.fchip'), count=$('#count'), more=$('#more'), empty=$('#empty'), sortBtn=$('#sort');
    var state={q:'',tag:'All',limit:20,oldest:false};
    var params=new URLSearchParams(location.search);
    if(params.get('tag'))state.tag=params.get('tag');
    if(params.get('q')){state.q=params.get('q');q.value=state.q}
    function render(){
      var s=state.q.trim().toLowerCase().replace(/^ep\.?\s*/,''), shown=0, matched=[];
      rows.forEach(function(li){
        var ok=(state.tag==='All'||li.dataset.tag===state.tag)&&(!s||li.dataset.search.indexOf(s)>-1||li.dataset.n===s);
        li.hidden=true; if(ok)matched.push(li);
      });
      if(state.oldest)matched.reverse();
      matched.forEach(function(li){list.appendChild(li)});
      matched.forEach(function(li,i){li.hidden=i>=state.limit});
      count.textContent=matched.length===1?'1 episode':matched.length+' episodes';
      more.hidden=matched.length<=state.limit; empty.hidden=matched.length>0;
      chips.forEach(function(c){c.setAttribute('aria-pressed',c.dataset.tag===state.tag?'true':'false')});
      sortBtn.textContent=state.oldest?'Oldest first':'Newest first';
    }
    q.addEventListener('input',function(){state.q=q.value;state.limit=20;render()});
    chips.forEach(function(c){c.addEventListener('click',function(){state.tag=c.dataset.tag;state.limit=20;render()})});
    more.addEventListener('click',function(){state.limit+=20;render()});
    sortBtn.addEventListener('click',function(){state.oldest=!state.oldest;render()});
    render();
  }

  // openness tabs
  var tabs=$$('[role=tab]');
  tabs.forEach(function(t){t.addEventListener('click',function(){
    tabs.forEach(function(x){x.setAttribute('aria-selected',x===t?'true':'false');$('#'+x.getAttribute('aria-controls')).hidden=x!==t});
  })});

  // myths
  $$('.myth').forEach(function(b){b.addEventListener('click',function(){var o=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',o?'false':'true')})});

  // listening path
  var path=$$('.path input');
  if(path.length){
    var saved=store('oap-path')||{};
    function upd(){var d=path.filter(function(i){return i.checked}).length;$('#pcount').textContent=d+' of '+path.length+' listened';$('#pbar').style.width=(d/path.length*100)+'%'}
    path.forEach(function(i){i.checked=!!saved[i.id];i.addEventListener('change',function(){saved[i.id]=i.checked;store('oap-path',saved);upd()})});
    upd();
  }

  // contact form -> email
  var cf=$('#contact-form');
  if(cf){cf.addEventListener('submit',function(e){e.preventDefault();
    var n=$('#nm').value,em=$('#em').value,ab=$('#ab').value,ms=$('#ms').value;
    var body=ms+'\n\n— '+n+(em?' ('+em+')':'');
    location.href='mailto:openadoptionproject@gmail.com?subject='+encodeURIComponent(ab+(n?' — '+n:''))+'&body='+encodeURIComponent(body);
    $('#cf-status').hidden=false;
  })}

  // copy link
  $$('[data-copy]').forEach(function(b){b.addEventListener('click',function(){
    var u=location.href, done=function(){b.textContent='Link copied ✓'};
    if(navigator.clipboard)navigator.clipboard.writeText(u).then(done,done);else done();
  })});
})();
