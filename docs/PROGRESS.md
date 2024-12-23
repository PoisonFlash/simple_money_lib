## Backlog
- [ ] Creating custom persistent currency collections
- [ ] Contexts as behaviour packages for Money
- [ ] Take-away serialization for custom currencies
- [ ] Non-persistent custom currency registration

## TODOs:
* Add documentation to Money class
* Add parsers documentation

## Notes
  
* All divisions ensure quantization, i.e., correct number of decimal digits is always preserved.
* __rmod__ operation like `5 % Currency("20 USD")` raises `TypeError`. In contrast with `moneyed` where: `5 % Currency(20, USD)` => `Money(1, USD)`.
