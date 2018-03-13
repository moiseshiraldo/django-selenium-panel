axios.defaults.headers.post['X-CSRFToken'] = window.csrf;

var Browser = Vue.extend({
    template: '#browser-template',
    data: function () {
        return {
            error: null,
            showTaskForm: false,
            taskForm: {
                // By default select first task of the list
                'task': Object.keys(this.tasks)[0],
                'server': null,
                'username': null,
                'password': null,
                'parents': this.tasks[Object.keys(this.tasks)[0]].parents,
                'arguments': {},
            },
            test: null,
        };
    },
    props: ['i', 'metadata', 'runTaskUrl', 'tasks', 'servers'],
    computed: {
        statusBadge: function () {
            switch(this.metadata.status) {
                case "Running":
                    return "badge-success";
                case "Failed":
                    return "badge-danger";
                default:
                    return "badge-secondary";
            }
        }
    },
    watch: {
        'taskForm.server': function (val) {
            this.taskForm.username = this.servers[val].username;
            this.taskForm.password = this.servers[val].password;
        },
        'taskForm.task': function (val) {
            this.taskForm.parents = this.tasks[val].parents;
        },
        'taskForm.parents': function(val) {
            if (val.length === 0) return;
            var oldest_parent = this.tasks[this.taskForm.task].parents.length;
            for (var i = 0; i < val.length; i++) {
                index = this.tasks[
                    this.taskForm.task
                ].parents.indexOf(val[i]);
                if (index < oldest_parent) oldest_parent = index;
            }
            must_select =  this.tasks[this.taskForm.task].parents.slice(
                oldest_parent
            );
            if ( must_select.length !== val.length ) {
                this.taskForm.parents = must_select;
            }
        },
    },
    methods: {
        runTask: function(e) {
            var component = this;
            formData = component.taskForm;
            formData['service_url'] = component.metadata.service_url;
            axios.post(config.urls.run_task,
                formData
            ).then(function (response) {
                component.error = null;
                component.metadata.status = "Running";
                component.showTaskForm = false;
            }).catch(function (error) {
                component.showTaskForm = false;
                component.error = "An unexpected error occurred.\
                              Please try again later.";
            });
        },
        showArgument: function(argument, task) {
            firstParent = this.tasks[task].parents.slice(-1)[0];
            parentSelected = this.taskForm.parents.indexOf(firstParent) === -1;
            if ( !argument.from_parent || parentSelected ) {
                return true;
            } else {
                return false;
            }
        },
    },
    mounted: function () {
        this.taskForm.server = "default";
    }
})

new Vue({
    el: '#browser-accordion',
    data: {
        browsers: [],
        error: null,
        tasks: config.tasks,
        servers: config.servers,
        urls: config.urls,
    },
    components: {
      browser: Browser,
    },
    methods: {
        updateBrowsers: function () {
            var component = this;
            axios.get(
                component.urls.browser_list
            ).then(function (response) {
                component.error = null;
                // Update listed browsers status
                for (var i = 0; i < component.browsers.length; i++) {
                    browser = component.browsers[i];
                    if ( browser.service_url in response.data) {
                        var status = response.data[browser.service_url].status;
                        browser.status = status;
                    } else {
                        component.browsers.splice(i, 1);
                    }
                }
                // Push new connected browsers to the component
                var connectedBrowsers = Object.keys(response.data);
                for (var i = 0; i < connectedBrowsers.length; i++) {
                    index = component.browsers.findIndex(
                        b => b.service_url === connectedBrowsers[i]
                    );
                    if (index === -1) {
                        component.browsers.push(
                            response.data[connectedBrowsers[i]]
                        );
                    }
                }
            }).catch(function (error) {
                component.error = "An unexpected error occurred.\
                                   Please try again later.";
            });
        },
    },
    mounted: function () {
        this.updateBrowsers();
        setInterval(function () {
            this.updateBrowsers();
        }.bind(this), 5000);
    }
});
