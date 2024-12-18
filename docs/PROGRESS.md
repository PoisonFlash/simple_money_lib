## Features
- [ ] Reintegrate ComplexParser
- [ ] Creating custom persistent currency collections
- [ ] Contexts as behaviour packages for Money

## TODOs:
* 
* Add documentation to Money class
* Add parsers documentation

## Consider
* operations like __add__ return NotImplemented for mismatched currencies rather than raising a TypeError
* The code assumes either a global or thread-local parser is always available. Should there be a fallback mechanism or error for missing parsers?
* Some method comments could be expanded for clarity, particularly in arithmetic and comparison operations.
* Custom exceptions (e.g., InvalidAmountError, InvalidCurrencyError) could improve clarity over generic exceptions like TypeError or ValueError.
* Replace rounding logic with 'with' type logic, instead of thread based

## Notes
* In-place operations (`+=, -=`) are not implemented to preserve immutability and thread safety. When performing `money1 += money2`, a new instance of `Money` is created, and money1 is updated to reference this new instance. The original `money1` object remains unchanged.  
* All divisions ensure quantization, i.e., correct number of decimal digits is always preserved.
* __rmod__ operation like `5 % Currency("20 USD")` raises `TypeError`. In contrast with `moneyed` where: `5 % Currency(20, USD)` => `Money(1, USD)`.
