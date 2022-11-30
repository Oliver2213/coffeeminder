# coffeeminder

_Automatic shut-off and probably other coffeemaker niceties for homeassistant._

## Installation

Download the `coffeeminder` directory from inside the `apps` directory here to your local `apps` directory, then add the configuration to enable the `coffeeminder` module.  
Or add as a repository in hacs if.

## App configuration

```yaml
coffeeminder:
  module: coffeeminder
  class: Coffeeminder
  constrain_input_boolean: input_boolean.coffeeminder
  coffee_switch: switch.coffee_maker_on_off
  # uses input_number.coffeeminder_minutes in homeassistant.
```

key | optional | type | default | description
-- | -- | -- | -- | --
`module` | False | string | | The module name of the app.
`class` | False | string | | The name of the Class.
