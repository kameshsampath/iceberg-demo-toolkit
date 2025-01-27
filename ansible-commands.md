```shell
ansible-galaxy collection install amazon.aws
```


## Setup 

```
ansible-playbook playbook.yml --tags setup
```

## Cleanup 

```
ansible-playbook playbook.yml --tags cleanup
```