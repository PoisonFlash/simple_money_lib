## Features
- [ ] Implement abstract parser logic
- [ ] Implement simple default parser

## TODOs:
* Implement contexts
* Implement get_default_currency from context
* Add documentation to Money class

## Completed Tasks


## Notes
* In-place operations (`+=, -=`) are not implemented to preserve immutability and thread safety. When performing `money1 += money2`, a new instance of `Money` is created, and money1 is updated to reference this new instance. The original `money1` object remains unchanged.  
* All divisions ensure quantization, i.e., correct number of decimal digits is always preserved.
* __rmod__ operation like `5 % Currency("20 USD")` raises `TypeError`. In contrast with `moneyed` where: `5 % Currency(20, USD)` => `Money(1, USD)`.
