## Backlog
- [ ] Creating custom persistent currency collections
- [ ] Contexts as behaviour packages for Money
- [ ] Localization: integrating Babel or a similar library for localized currency names and formatting
- [ ] More custom exceptions
- [ ] Consider replacing rounding logic with 'with' type logic, instead of thread based

## TODOs:
* Add documentation to Money class
* Add parsers documentation

## Notes
* In-place operations (`+=, -=`) are not implemented to preserve immutability and thread safety. When performing `money1 += money2`, a new instance of `Money` is created, and money1 is updated to reference this new instance. The original `money1` object remains unchanged.  
* All divisions ensure quantization, i.e., correct number of decimal digits is always preserved.
* __rmod__ operation like `5 % Currency("20 USD")` raises `TypeError`. In contrast with `moneyed` where: `5 % Currency(20, USD)` => `Money(1, USD)`.
