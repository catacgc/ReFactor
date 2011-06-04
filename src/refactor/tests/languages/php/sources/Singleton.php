<?php

namespace Mach\Pattern;

/**
 * Singleton Design Pattern Abstract Class
 * 
 * @author Rares Mirica
 * @version 1.0
 * @package Mach
 * @subpackage Pattern
 */
abstract class Singleton
{

    protected static $_instances = array();

    /**
     * Restrictive __constructor cannot be overridden
     * 
     * @param $args
     */
    private final function __construct($args = null)
    {
        call_user_func_array(array($this, '__init'), $args);
    }

    /**
     * Restrictive clone
     */
    private final function __clone()
    {

    }

    /**
     * Alternate constructor 
     */
    protected function __init()
    {

    }

    /**
     * Get instance of the Singleton class
     * 
     * @return \Mach\Pattern\Singleton
     */
    public static function getInstance()
    {
        $class = get_called_class();
        if(!array_key_exists($class, self::$_instances)
            || !self::$_instances[$class] instanceof static) {
            $args = func_get_args();
            self::$_instances[$class] = new static($args);
        }

        return self::$_instances[$class];
    }

}