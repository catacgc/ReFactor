<?php

namespace Mach;

/**
 * Config object
 *
 * History:
 *  2.1 - CC: apc cache support
 *  2.2 - CC: environment support and fallback sections
 *  2.3 - CC: get rid of \Zend_Config methods and variables internally
 *
 * @author Rares Vlasceanu
 * @author Catalin Costache
 * @package Mach
 * @subpackage Config
 * @version 2.3
 */
class Config extends \Zend_Config implements \ArrayAccess, \Countable, \Iterator
{
    /**
     * Contains array of configuration data
     *
     * @var array
     */
    protected $_data;
    protected $_index;
    protected $_count;

    private $isCacheable = null;

    private static $_instance;
    protected $globalPath;
    protected $modulePathSpec;
    protected $loadedFiles = array();

    protected $env = null;
    protected $defaultSection = null;
    protected $fallbackSectionsMap = array();

    const CACHE_KEY_PREFIX = '[config] ';

    /**
     * Config provides a property based interface to
     * an array. The data are read-only unless $allowModifications
     * is set to true on construction.
     *
     * Config also implements Countable and Iterator to
     * facilitate easy access to the data.
     *
     * @param  array   $array
     * @param  boolean $allowModifications
     * @return void
     */
    public function __construct(array $array)
    {
        $this->_loadedSection = null;
        $this->_index = 0;
        $this->_data = array();
        foreach ($array as $key => $value) {
            if (is_array($value)) {
                $this->_data[$key] = new self($value);
            } else {
                $this->_data[$key] = $value;
            }
        }
        $this->_count = count($this->_data);
    }

    /**
     * Instance getter
     *
     * @return Config
     */
    public static function getInstance()
    {
        if (!self::$_instance instanceof self) {
            self::$_instance = new self(array(), true);
        }

        return self::$_instance;
    }

    /**
     * Set instance options
     *
     * @param array $options
     */
    public function setOptions(array $options = array())
    {
        if (isset($options['globalPath'])) {
            $this->globalPath = $options['globalPath'];
        }
        if (isset($options['modulePathSpec'])) {
            $this->modulePathSpec = $options['modulePathSpec'];
        }
    }

    /**
     * Alias for \Mach\Config::getInstance
     *
     * @param string $ini
     * @param string $module
     * @return Config
     */
    public static function init($ini = null, $module = null)
    {
        $inst = self::getInstance();
        return $inst->load($ini, $module);
    }

    /**
     * Load config file
     *
     * @param string $configFile
     * @return Mach\Config
     */
    public function load($configFile = null, $module = null)
    {
        if (empty($configFile) || $this->isLoaded($configFile, $module)) {
            return $this;
        }

        $fileName = $this->getFullPathTo($configFile, $module);
        if (!$this->loadFromCache($fileName)) {
            $this->merge($this->readIniFile($fileName, $this->getEnv()));
        }
        $this->loadedFiles[] = $fileName;

        return $this;
    }

    /**
     * Check if config file is loaded
     *
     * @param string $configFile
     * @param string | null $module
     * @return boolean
     */
    public function isLoaded($configFile, $module = null)
    {
        $fileName = $this->getFullPathTo($configFile, $module);

        return in_array($fileName, $this->loadedFiles);
    }

    /**
     * Get full path to config file
     *
     * @param string $configFile
     * @param string | null $module
     * @return string
     */
    protected function getFullPathTo($configFile, $module = null)
    {
        if ($module === null) {
            $path = $this->globalPath;
        } else {
            $path = sprintf($this->modulePathSpec, $module);
        }

        return $path . DIRECTORY_SEPARATOR . $configFile;
    }

    public function setEnv($env) {
        $this->env = $env;
    }

    public function getEnv() {
        return $this->env ?: APPLICATION_ENV;
    }

    /**
     * Add a default env fallback
     * Any time you will try to load a config file wich has no section for the
     * given env, this default env will be used if no explicit fallback
     * is defined for that env
     *
     * @param string $section
     */
    public function setDefaultFallbackEnv($section) {
        $this->defaultSection = $section;
    }

    /**
     * Add an explicit env fallback
     * This fallback will be used if the env definition is not present in the
     * config file
     *
     * @param string $section
     * @param string $fallBackSection
     */
    public function addFallbackEnv($section, $fallBackSection) {
        $this->fallbackSectionsMap[$section] = $fallBackSection;
    }

    /**
     * Return the fallback env for this env
     * If no env fallback is found, return the default fallback env
     * If no default fallback env is found, throw exception
     * @param string $env
     * @return string
     */
    public function getFallbackEnv($env) {
        if(isset($this->fallbackSectionsMap[$env]) && $this->fallbackSectionsMap[$env] != $env) {
            return $this->fallbackSectionsMap[$env];
        }

        if($this->defaultSection && $this->defaultSection != $env) {
            return $this->defaultSection;
        }

        throw new \InvalidArgumentException("A fallback for $env environment not found.
                Use [setDefaultFallbackEnv] and [addFallbackEnv] to set the fallbacks");
    }

    /**
     * Read config file into a Config_Ini object
     *
     * @param string $fileName
     * @return array
     */
    protected function readIniFile($fileName, $env)
    {
        if (!file_exists($fileName)) {
            throw new \InvalidArgumentException("Unable to read file! ({$fileName})");
        }

        try {
            $result = new \Zend_Config_Ini($fileName, $env);
        } catch(\Zend_Config_Exception $ex) {
            $result = $this->readIniFile($fileName, $this->getFallbackEnv($env));
        }
        if(is_array($result)) {
            return $result;
        }
        return $result->toArray();
    }

    public function useCache($boolean) {
        $this->isCacheable = $boolean;
    }

    public function usingCache() {
        if($this->isCacheable === null) {
            return Env::isProduction();
        }
        return $this->isCacheable;
    }

    /**
     * If we are on a production environment then we will use
     * apc for config cache
     *
     * @param string $fileName
     * @return boolean
     */
    protected function loadFromCache($fileName)
    {
        if (!$this->usingCache()) {
            return false;
        }

        $cacheKey = self::CACHE_KEY_PREFIX . $fileName . ' [' . $this->getEnv(). ']';
        $configArray = apc_fetch($cacheKey);
        if ($configArray === false) {
            $configArray = $this->readIniFile($fileName, $this->getEnv());
            apc_store($cacheKey, $configArray);
        }

        $this->merge($configArray);
        return true;
    }

    /**
     * Merge another Config with this Config
     * and convert \Zend_Cofig to Config
     * @param array $merge
     * @return Mach\Config
     */
    public function merge(array $merge)
    {
        foreach ($merge as $key => $arrayItem) {
            if (array_key_exists($key, $this->_data)) {
                if ($this->$key instanceof \Zend_Config) {
                    $this->$key = $this->$key->merge((array)$arrayItem);
                } else {
                    if (is_array($arrayItem)) {
                        $this->$key = new self($arrayItem);
                    } else {
                        $this->$key = $arrayItem;
                    }
                }
            } else {
                if (is_array($arrayItem)) {
                    $this->$key = new self($arrayItem);
                } else {
                    $this->$key = $arrayItem;
                }
            }
        }

        return $this;
    }

    /**
     * Retrieve a value and return $default if there is no element set.
     *
     * @param string $name
     * @param mixed $default
     * @return mixed
     */
    public function get($name, $default = null)
    {
        $result = $default;
        if (array_key_exists($name, $this->_data)) {
            $result = $this->_data[$name];
        }
        return $result;
    }

    /**
     * Magic function so that $obj->value will work.
     *
     * @param string $name
     * @return mixed
     */
    public function __get($name)
    {
        return $this->get($name);
    }

    /**
     * @param  string $name
     * @param  mixed  $value
     * @return void
     */
    public function __set($name, $value)
    {
        if (is_array($value)) {
            $this->_data[$name] = new self($value);
        } else {
            $this->_data[$name] = $value;
        }
        $this->_count = count($this->_data);

    }

    /**
     * Return an associative array of the stored data.
     *
     * @return array
     */
    public function toArray()
    {
        $array = array();
        $data = $this->_data;
        foreach ($data as $key => $value) {
            if ($value instanceof Config) {
                $array[$key] = $value->toArray();
            } else {
                $array[$key] = $value;
            }
        }
        return $array;
    }

    public function offsetExists($offset)
    {
        return isset($this->_data[$offset]);
    }

    public function offsetGet($offset)
    {
        if (!isset($this->_data[$offset])) {
            return null;
        }

        if ($this->_data[$offset] instanceof Config) {
            return $this->_data[$offset]->toArray();
        }
        return $this->_data[$offset];
    }

    public function offsetSet($offset, $value)
    {
        $this->_data[$offset] = $value;
    }

    public function offsetUnset($offset)
    {
        unset($this->_data[$offset]);
    }

    public function count() {
        return $this->_count;
    }

    public function current() {
        return current($this->_data);
    }

    public function key() {
        return key($this->_data);
    }

    public function next() {
        next($this->_data);
        $this->_index++;
    }

    public function rewind() {
        reset($this->_data);
        $this->_index = 0;
    }

    public function valid() {
        return $this->_index < $this->_count;
    }

}
