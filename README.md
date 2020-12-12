### requirement: 
 - python3
 - jq *command tool*

### install and run as a daemon
steps:
1. copy file `mpool-keeper.py` to server which have authority to access your lotus full node.
2. change `user` to same user with your lotus daemons, as `mpool-keeper.py` needs same environment variables as your lotus daemons.
3. then, run bellow commands
``` 
$ chmod +x mpool-keeper.py
$ ./mpool-keeper.py > mpool-keeper.log  2>&1 &
```

